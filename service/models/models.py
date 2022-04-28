import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import UniqueConstraint


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField('название', max_length=255)
    description = models.TextField('описание', blank=True)

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = 'жанр'
        verbose_name_plural = 'жанры'

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.TextField('ФИО', blank=True)
    birth_date = models.DateField('день рождения')

    class Meta:
        db_table = "content\".\"person"
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'

    def __str__(self):
        return self.full_name


class Filmwork(UUIDMixin, TimeStampedMixin):

    class FilmworksType(models.TextChoices):
        MOVIE = 'MV', _('movie')
        TV_SHOW = 'TV', _('tv_show')

    title = models.CharField(_('title'), max_length=255)
    description = models.TextField('описание', blank=True)
    creation_date = models.DateField('дата создания')
    certificate = models.TextField('сертификат', blank=True)
    file_path = models.TextField('путь к файлу', blank=True)
    rating = models.FloatField('рейтинг', blank=True,
                               validators=[MinValueValidator(0),
                                           MaxValueValidator(100)])
    type = models.CharField(_('type'),
                            choices=FilmworksType.choices,
                            default=FilmworksType.MOVIE,
                            max_length=2)
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    persons = models.ManyToManyField(Person, through='PersonFilmwork')

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = 'Кинопроизведение'
        verbose_name_plural = 'Кинопроизведения'

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        verbose_name = 'Жанр фильма'
        indexes = [
            models.Index(fields=['film_work'], name='film_work_idx'),
        ]
        UniqueConstraint(fields=['film_work', 'genre'], name='unique_film_genre')


class PersonFilmwork(UUIDMixin):
    class PersonFilmworksType(models.TextChoices):
        FILMMAKER = 'FM', _('filmmaker')
        SCREENWRITER = 'SW', _('screenwriter')
        ACTOR = 'AC', _('actor')

    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    role = models.CharField(_('role'),
                            choices=PersonFilmworksType.choices,
                            default=PersonFilmworksType.ACTOR,
                            max_length=2
                            )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        verbose_name = 'Участник кинопроизведения'
        verbose_name_plural = 'Участники кинопроизведения'
        indexes = [
            models.Index(fields=['film_work', 'person'], name='film_work_person_idx'),
        ]
        UniqueConstraint(fields=['film_work', 'person', 'role'], name='unique_person_role')
