from django.core.management.base import BaseCommand
from payments.models import Family, Cohort

class Command(BaseCommand):
    help = 'Sets up initial families and cohorts for MMUSDA'

    def handle(self, *args, **kwargs):
        # Create families
        families = [
            {'name': 'Heralds', 'description': 'Heralds Family'},
            {'name': 'Royal', 'description': 'Royal Family'},
            {'name': 'Aroma of Christ', 'description': 'Aroma of Christ Family'},
            {'name': 'Eagles', 'description': 'Eagles Family'},
            {'name': 'Pilgrims', 'description': 'Pilgrims Family'},
            {'name': 'Humble', 'description': 'Humble Family'},
            {'name': 'Emerald', 'description': 'Emerald Family'},
        ]

        for family_data in families:
            family, created = Family.objects.get_or_create(
                name=family_data['name'],
                defaults={'description': family_data['description']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created family: {family.name}'))
            else:
                self.stdout.write(f'Family already exists: {family.name}')

        # Create cohorts (2019-2025)
        cohorts = [
            {'name': 'Class of 2019', 'year': 2019, 'description': 'MMUSDA Class of 2019'},
            {'name': 'Class of 2020', 'year': 2020, 'description': 'MMUSDA Class of 2020'},
            {'name': 'Class of 2021', 'year': 2021, 'description': 'MMUSDA Class of 2021'},
            {'name': 'Class of 2022', 'year': 2022, 'description': 'MMUSDA Class of 2022'},
            {'name': 'Class of 2023', 'year': 2023, 'description': 'MMUSDA Class of 2023'},
            {'name': 'Class of 2024', 'year': 2024, 'description': 'MMUSDA Class of 2024'},
            {'name': 'Class of 2025', 'year': 2025, 'description': 'MMUSDA Class of 2025'},
        ]

        for cohort_data in cohorts:
            cohort, created = Cohort.objects.get_or_create(
                year=cohort_data['year'],
                defaults={
                    'name': cohort_data['name'],
                    'description': cohort_data['description']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created cohort: {cohort.name}'))
            else:
                self.stdout.write(f'Cohort already exists: {cohort.name}') 