from django.shortcuts import render
from catalog.models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from catalog.forms import RenewBookForm

import datetime

# Create your views here.

def index(request):
	
	num_books = Book.objects.all().count()
	num_instances = BookInstance.objects.all().count()

	# avialable books
	num_instances_available = BookInstance.objects.filter(status__exact="a").count()

	num_authors = Author.objects.all().count()

	num_visits = request.session.get("num_visits", 0)
	request.session['num_visits'] = num_visits + 1

	context = {
		"num_books": num_books,
		"num_instances": num_instances,
		"num_instances_available": num_instances_available,
		"num_authors": num_authors,
		"num_visits": num_visits,
	}

	return render(request, "index.html", context=context) 


class BookListView(LoginRequiredMixin, generic.ListView):
	model = Book
	paginate_by = 10

class BookDetailView(LoginRequiredMixin, generic.DetailView):
	model = Book

class AuthorListView(LoginRequiredMixin, generic.ListView):
	model = Author 
	paginate_by = 10

class AuthorDetailView(LoginRequiredMixin, generic.DetailView):
	model = Author 

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
	model = BookInstance
	template_name = "catalog/bookinstance_list_borrowed_user.html"
	paginate_by = 10

	def get_queryset(self):
		return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact="o").order_by("due_back")

class AllLoanedBooksListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
	model = BookInstance
	template_name = "catalog/bookinstance_list_borrowed_user.html"
	paginate_by = 10
	permission_required = 'catalog.can_mark_returned'

	def get_queryset(self):
		return BookInstance.objects.filter(status__exact="o").order_by("due_back")

def renew_book_librarian(request, pk):
	book_instance = get_object_or_404(BookInstance, pk=pk)

	if request.method == "POST":
		form = RenewBookForm(request.POST)

		if form.is_valid():
			book_instance.due_back = form.cleaned_data["renewal_date"]
			book_instance.save()

			return HttpResponseRedirect(reverse("all-borrowed"))

	else:
		proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
		form = RenewBookForm(initial={"renewal_date": proposed_renewal_date})

	context = {
		"form" : form,
		"book_instance" : book_instance
	}

	return render(request, "catalog/book_renew_librarian.html", context)

class AuthorCreate(CreateView):
	model = Author
	fields = '__all__'

class AuthorUpdate(UpdateView):
	model = Author
	fields = ["first_name", "last_name", "date_of_birth", "date_of_death"]	

class AuthorDelete(DeleteView):
	model = Author
	success_url = reverse_lazy('authors')