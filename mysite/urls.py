import views

urlpatterns = {
    # '/': views.index_view,
    # '/contacts/': views.contacts_view,
    # '/categories/': views.categories_view,
    # '/create_category/': views.create_category,
    '/courses/': views.Courses(),
    # '/create_course/': views.create_course,
    '/style.css/': views.css_view,
    '/categories/': views.CategoryListView(),
    '/student-list/': views.StudentListView(),
}
urlpatterns.update(views.urlpatterns)
