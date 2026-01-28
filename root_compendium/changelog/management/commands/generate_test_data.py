"""
Django management command to generate test data for the changelog app.
Usage: python manage.py generate_test_data
"""

# AI generated 
# Test data generation

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from changelog.models import Update
from datetime import timedelta


class Command(BaseCommand):
    help = 'Generates 10 test update records for development and testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing test data before generating new data',
        )

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Get the first superuser or create a test user
        try:
            author = User.objects.filter(is_superuser=True).first()
            if not author:
                self.stdout.write(self.style.WARNING(
                    'No superuser found. Please create a superuser first with: python manage.py createsuperuser'
                ))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting user: {e}'))
            return

        # Clear existing test data if requested
        if options['clear']:
            deleted_count = Update.objects.filter(title__startswith='Test Update').delete()[0]
            self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_count} existing test records'))

        # Generate 10 test updates with varied data
        test_updates = [
            {
                'title': 'Test Update 1 - Major Feature Release',
                'slug': 'test-update-1-major-feature-release',
                'body': 'Introduced comprehensive new dashboard with real-time analytics and reporting capabilities. This update includes enhanced visualization tools, improved data processing performance, and a redesigned user interface for better accessibility.',
                'major_version': 5,
                'current_patch': 0,
                'bug_fix': 'a',
                'change_type': 'M',
            },
            {
                'title': 'Test Update 2 - Authentication System Overhaul',
                'slug': 'test-update-2-authentication-system',
                'body': 'Complete redesign of the authentication system with OAuth2 support, two-factor authentication, and improved security measures. Users can now sign in with multiple providers including Google, GitHub, and Microsoft.',
                'major_version': 4,
                'current_patch': 5,
                'bug_fix': 'a',
                'change_type': 'M',
            },
            {
                'title': 'Test Update 3 - Performance Improvements',
                'slug': 'test-update-3-performance-improvements',
                'body': 'Optimized database queries and implemented caching strategies resulting in 40% faster page load times. Background job processing has been enhanced with better queue management and error handling.',
                'major_version': 4,
                'current_patch': 2,
                'bug_fix': 'a',
                'change_type': 'P',
            },
            {
                'title': 'Test Update 4 - Bug Fix for Export Feature',
                'slug': 'test-update-4-bug-fix-export',
                'body': 'Fixed critical issue where large dataset exports would timeout. Export functionality now handles files up to 100MB without issues and includes progress indicators for better user experience.',
                'major_version': 4,
                'current_patch': 1,
                'bug_fix': 'c',
                'change_type': 'B',
            },
            {
                'title': 'Test Update 5 - UI Enhancement Update',
                'slug': 'test-update-5-ui-enhancement',
                'body': 'Refreshed user interface with modern design elements, improved accessibility features, and better mobile responsiveness. Added new color themes and customization options for personalized experiences.',
                'major_version': 4,
                'current_patch': 1,
                'bug_fix': 'a',
                'change_type': 'P',
            },
            {
                'title': 'Test Update 6 - API Version 3.0 Release',
                'slug': 'test-update-6-api-v3-release',
                'body': 'Launched new API with RESTful endpoints, GraphQL support, and comprehensive documentation. Backward compatibility maintained with deprecation warnings for old endpoints. Rate limiting and authentication improved.',
                'major_version': 3,
                'current_patch': 0,
                'bug_fix': 'a',
                'change_type': 'M',
            },
            {
                'title': 'Test Update 7 - Security Patch',
                'slug': 'test-update-7-security-patch',
                'body': 'Addressed multiple security vulnerabilities including XSS prevention, SQL injection protection, and CSRF token validation. All users are encouraged to update immediately to ensure system security.',
                'major_version': 2,
                'current_patch': 8,
                'bug_fix': 'b',
                'change_type': 'B',
            },
            {
                'title': 'Test Update 8 - Notification System Added',
                'slug': 'test-update-8-notification-system',
                'body': 'Implemented real-time notification system with email, SMS, and in-app alerts. Users can customize their notification preferences and set up custom triggers based on specific events and conditions.',
                'major_version': 2,
                'current_patch': 7,
                'bug_fix': 'a',
                'change_type': 'P',
            },
            {
                'title': 'Test Update 9 - Database Migration Complete',
                'slug': 'test-update-9-database-migration',
                'body': 'Successfully migrated to new database infrastructure with improved redundancy and backup systems. Performance benchmarks show 30% improvement in query response times and better scalability.',
                'major_version': 2,
                'current_patch': 5,
                'bug_fix': 'a',
                'change_type': 'M',
            },
            {
                'title': 'Test Update 10 - Minor Text Corrections',
                'slug': 'test-update-10-text-corrections',
                'body': 'Fixed various typos and grammatical errors throughout the application. Updated help documentation with clearer instructions and added new FAQ entries based on user feedback and support tickets.',
                'major_version': 2,
                'current_patch': 4,
                'bug_fix': 'a',
                'change_type': 'B',
            },
        ]

        created_count = 0
        for i, update_data in enumerate(test_updates):
            # Create update with staggered publish dates
            publish_date = timezone.now() - timedelta(days=(i * 2))
            
            update = Update.objects.create(
                title=update_data['title'],
                slug=update_data['slug'],
                body=update_data['body'],
                publish=publish_date,
                major_version=update_data['major_version'],
                current_patch=update_data['current_patch'],
                bug_fix=update_data['bug_fix'],
                change_type=update_data['change_type'],
                automated_post=False,
                status=Update.Status.PUBLISHED,
                author=author
            )
            created_count += 1
            self.stdout.write(self.style.SUCCESS(
                f'✓ Created: {update.title} - {update.version}'
            ))

        self.stdout.write(self.style.SUCCESS(
            f'\n{created_count} test updates created successfully!'
        ))
        self.stdout.write(self.style.WARNING(
            '\nTo clear test data later, run: python manage.py generate_test_data --clear'
        ))
