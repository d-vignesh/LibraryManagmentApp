from django.db import models
from django.urls import reverse
import uuid
from django.contrib.auth.models import User

from datetime import date 

# Create your models here.
class Genre(models.Model):
	"""model representing a book genre."""
	name = models.CharField(
		max_length=200, 
		help_text="enter a book genre(e.g. Sciece Fiction)"
	)

	def __str__(self):
		return self.name

class Language(models.Model):
	name = models.CharField(
		max_length=200,
		help_text="Enter the language that book is written in"
	)

	def __str__(self):
		return self.name

class Book(models.Model):
	title = models.CharField(max_length=200)
	author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
	summary = models.TextField(max_length=1000, help_text="Enter a brief description of the book")
	isbn = models.CharField("ISBN", max_length=13, 
						help_text="13 Character <a href='https://www.isbn-international.org/content/what-isbn'>ISBN number</a>")
	genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")
	language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return self.title

	def get_absolute_url(self):
		return reverse('book-detail', args=[str(self.id)])

	def display_genre(self):
		return ", ".join(genre.name for genre in self.genre.all()[:3])

	display_genre.short_description = "Genre"

class BookInstance(models.Model):
	"""model representing a specific copy of a book"""
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text="Unique ID for this particular book across whole library")
	book = models.ForeignKey("Book", on_delete=models.SET_NULL, null=True)
	imprint = models.CharField(max_length=200)
	due_back = models.DateField(null=True, blank=True)
	borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

	LOAN_STATUS = (
		("m", "Maintenance"),
		("o", "On loan"),
		("a", "Avialable"),
		("r", "Reserved"),
	)

	status = models.CharField(
		max_length=1,
		choices=LOAN_STATUS,
		blank=True,
		default="m",
		help_text="Book Avialability"
	)

	class Meta:
		ordering = ["due_back"]
		permissions = (("can_mark_returned", "Set book as returned"),)

	def __str__(self):
		return f"{self.id} ({self.book.title})"

	@property
	def is_overdue(self):
		if self.due_back and date.today() > self.due_back:
			return True
		return False

class Author(models.Model):
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	date_of_birth = models.DateField(null=True, blank=True)
	date_of_death = models.DateField('Died', null=True, blank=True)

	class Meta:
		ordering = ['last_name', 'first_name']

	def get_absolute_url(self):
		return reverse("author-detail", args=[str(self.id)])

	def __str__(self):
		return f"{self.first_name}, {self.last_name}"

