from django.db.models.query import QuerySet

from workplaces.models import Category, TopCategory, Workplace


def categoryExistAsTopCategory(
    categoryName: str, topCategories: list[dict]
) -> int | None:
    index = 0
    for topCategory in topCategories:
        isCategoryInAnyTopCategory = any(
            [cat.lower() == categoryName.lower() for cat in topCategory["categories"]]
        )
        if isCategoryInAnyTopCategory:
            return index
        index += 1
    return None


# TODO Make over categories and auto create them if they do not exist
def getWorkplaceTopCategories():
    topCategories = []

    workplaces = Workplace.objects.filter(deletedAt__isnull=True)
    for workplace in workplaces:
        workplaceCategories = workplace.categories.all()
        workplaceCategoryNames = [cat.name for cat in workplaceCategories]

        for category in workplaceCategories:
            topCategoryIndex = categoryExistAsTopCategory(category.name, topCategories)
            if topCategoryIndex is not None:
                for category in workplaceCategories:
                    # Add the not existing categories to the top category
                    if (
                        category.name
                        not in topCategories[topCategoryIndex]["categories"]
                    ):
                        topCategories[topCategoryIndex]["categories"].append(
                            category.name
                        )
                break

            topCategories.append(
                {"name": category.name, "categories": workplaceCategoryNames}
            )

    # Make sure we don't have any topCategories with only itself as category
    filteredTopCategories = []
    for topCategory in topCategories:
        if len(topCategory["categories"]) > 1:
            filteredTopCategories.append(topCategory)
    topCategories = filteredTopCategories

    return topCategories


def createTopCategoriesFromWorkplaces():
    topCategoriesData = getWorkplaceTopCategories()

    print("Creating TopCategories from workplaces...")
    for topCategoryData in topCategoriesData:
        categories = []
        for categoryName in topCategoryData["categories"]:
            category, created = Category.objects.get_or_create(name=categoryName)
            categories.append(category)

        topCategory, created = TopCategory.objects.get_or_create(
            name=topCategoryData["name"]
        )
        topCategory.categories.set(categories)
        topCategory.save()
        print(f"Created/Updated TopCategory: {topCategory.name}")
    print("Done creating TopCategories from workplaces.")
