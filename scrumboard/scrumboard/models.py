from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
#  /*------------------------------------------------------------------------*/
#   * Progetto - Ingegneria del Software - models.py
#  /*------------------------------------------------------------------------*/
#   * Nome:         - Scrumboard
#   * Descrizione:  - Applicazione Web per la gestione di una board scrum
#   * Autori:       - Pilloni Raffaele  - 65151
#                   - Meloni Giacomo    - 65181
#                   - Ziantoni Stefano  - 65197
#                   - Ibba Andrea       - 65258
#  /*------------------------------------------------------------------------*/

"""
    - SCRUMBOARD -
"""
class Board(models.Model):
    name = models.CharField(max_length=50)
    users = models.ManyToManyField(User)

    # url per arrivare alla vista scrumboard
    def get_absolute_url(self):
        return reverse('scrum-board', args=[str(self.id)])

    # url per arrivare alla vista aggiungi user alla board
    def get_addUserToBoard_url(self):
        return reverse('add-user-to-board', args=[str(self.id)])

    # url per richiedere la' aggiunta/eliminazione di un user con una post
    def get_addUserToBoardPost_url(self):
        return reverse('add-user-to-board-post')

    # url per arrivare alla vista crea colonna
    def get_addColumn_url(self):
        return reverse('add-column', args=[str(self.id)])

    # url per richiedere la' creazione di una colonna nella board con una post
    def get_addColumnPost_url(self):
        return reverse('add-column-post')

    # url per richiedere l'eliminazione di una colonna della board con una post
    def get_deleteColumn_url(self):
        return reverse('del-column')

    # url per arrivare alla vista burndown
    def get_burndown_url(self):
        return reverse('burndown', args=[self.id])

"""
    - COLONNA -
"""
class Column(models.Model):
    name = models.CharField(max_length=50)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)

    # url per arrivare alla vista colonna
    def get_absolute_url(self):
        return reverse('column', args=[str(self.board.id), str(self.id)])

    # url richiesta modifica nome con una post
    def get_modifyNamePost_url(self):
        return reverse('post-column')

    # url per raggiungere addi card dalla vista colonna
    def get_addCardReturnColumn_url(self):
        return reverse('add-card', args=[str(self.board.id), str(self.id), 'column'])

    # url utilizzato per raggiungere add card da board
    def get_addCardReturnBoard_url(self):
        return reverse('add-card', args=[str(self.board.id), str(self.id), 'scrumboard'])

    # url utilizzato per fare la richiesta post dell' aggiungi card
    def get_addCardPost_url(self):
        return reverse('add-card-post')
    # url utilizzato per richiedere l'eliminazione card con una post
    def get_deleteCard_url(self):
        return reverse('post-column')

"""
    - COLONNA -
"""
class Card(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    dateCreation = models.DateTimeField(default=timezone.now)
    storyPoints = models.IntegerField()
    dateExpire = models.DateField()
    column = models.ForeignKey(Column, on_delete=models.CASCADE)
    users = models.ManyToManyField(User)

    # url utilizzato per raggiungere la vista card
    def get_absolute_url(self):
        return reverse('card', args=[str(self.column.board.id), str(self.column.id), str(self.id)])

    # url utilizzato per fare la richiesta modifica dati card con una post
    def get_modifyCardPost_url(self):
        return reverse('post-card')

    # url utilizzato per fare la richiesta agiungi/elimina utente  alla card con una post
    def get_addUserToCardPost_url(self):
        return reverse('post-card')
