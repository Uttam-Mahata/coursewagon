from playwright.sync_api import Page, expect

def test_homepage_loads(page: Page):
    """
    This test verifies that the home page of the application loads correctly
    after the migration to standalone components.
    """
    # 1. Arrange: Go to the application's home page.
    page.goto("http://localhost:4200")

    # 2. Assert: Confirm the page title is correct.
    # This helps ensure the correct application is running.
    expect(page).to_have_title("CourseWagon")

    # 3. Assert: Check for a key element on the home page.
    # We'll look for the main heading.
    heading = page.get_by_role("heading", name="The Ultimate Course Authoring Tool")
    expect(heading).to_be_visible()

    # 4. Screenshot: Capture the final result for visual verification.
    page.screenshot(path="jules-scratch/verification/homepage.png")