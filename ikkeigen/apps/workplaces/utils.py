import requests
from django.db.models import Q
from django.db.models.query import QuerySet

from workplaces.models import Category, Workplace


def createWorkplaceByVATNumber(vatNumber: str) -> None:
    """
    Returns a queryset of workplaces matching the given VAT number.
    """
    search = vatNumber.strip()
    url = f"https://pms.laerepladsen.dk/api/soeg-opslag-kort/-1/-1?fritekst={search}&aftaleFilter=alle&medarbejdereFilter=alle&zoom=1&north=56.43007523471859&south=55.215764803933716&east=15.529157706956447&west=6.954356941849672"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        results = data.get("laeresteder", [])
        maxResults = 15
        results = results[:maxResults]
        createdNew = False

        for workplace in results:
            vat = workplace.get("cvr")
            name = workplace.get("navn", "")
            brancher = workplace.get("brancher", [])
            address = workplace.get("adresse", "")

            categories = []
            for category in brancher:
                categoryName = category.get("tekst", "")
                if not categoryName:
                    continue

                categoryObj, created = Category.objects.get_or_create(name=categoryName)
                categories.append(categoryObj)

            workplaceObj, created = Workplace.objects.get_or_create(
                vat=vat, address=address, defaults={"name": name}
            )
            workplaceObj.categories.set(categories)
            workplaceObj.save()

            if created:
                createdNew = True
        return createdNew
    except (requests.RequestException, ValueError):
        return False
