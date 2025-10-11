from playwright.sync_api import Page, expect

def test_responsive_design(page: Page):
    # My Courses Dashboard
    page.goto("http://localhost:4200/my-courses-dashboard")
    page.set_viewport_size({"width": 375, "height": 667})
    page.screenshot(path="jules-scratch/verification/my-courses-dashboard-mobile.png")
    page.set_viewport_size({"width": 768, "height": 1024})
    page.screenshot(path="jules-scratch/verification/my-courses-dashboard-tablet.png")
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.screenshot(path="jules-scratch/verification/my-courses-dashboard-desktop.png")

    # Browse Courses
    page.goto("http://localhost:4200/course-catalog")
    page.set_viewport_size({"width": 375, "height": 667})
    page.screenshot(path="jules-scratch/verification/course-catalog-mobile.png")
    page.set_viewport_size({"width": 768, "height": 1024})
    page.screenshot(path="jules-scratch/verification/course-catalog-tablet.png")
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.screenshot(path="jules-scratch/verification/course-catalog-desktop.png")

    # My Learning
    page.goto("http://localhost:4200/learner-dashboard")
    page.set_viewport_size({"width": 375, "height": 667})
    page.screenshot(path="jules-scratch/verification/learner-dashboard-mobile.png")
    page.set_viewport_size({"width": 768, "height": 1024})
    page.screenshot(path="jules-scratch/verification/learner-dashboard-tablet.png")
    page.set_viewport_size({"width": 1920, "height": 1080})
    page.screenshot(path="jules-scratch/verification/learner-dashboard-desktop.png")