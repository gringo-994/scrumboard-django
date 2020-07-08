from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.forms import BooleanField
from models import Board, Column, Card
from costant.costants import MODIFY_ACTIVATE_COLUMN, MODIFY_ACTIVATE_CARD
#  /*------------------------------------------------------------------------*/
#   * Progetto - Ingegneria del Software - forms.py
#  /*------------------------------------------------------------------------*/
#   * Nome:         - Scrumboard
#   * Descrizione:  - Applicazione Web per la gestione di una board scrum
#   * Autori:       - Pilloni Raffaele  - 65151
#                   - Meloni Giacomo    - 65181
#                   - Ziantoni Stefano  - 65197
#                   - Ibba Andrea       - 65258
#  /*------------------------------------------------------------------------*/

"""
    - FORM GESTIONE ACCOUNT -   
"""
# form di sign in
class SignInForm(forms.Form):
    next = forms.CharField(widget=forms.HiddenInput(), label='')
    username = forms.CharField(label='username', max_length=50, widget=forms.TextInput(attrs={'class': 'field'}))
    password = forms.CharField(label='password', max_length=50, widget=forms.PasswordInput(attrs={'class': 'field'}))

    def clean(self):# restitusce errore se l userneme non esiste o la password e errata
        cleaned_data = super(SignInForm, self).clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            raise forms.ValidationError('*username o password errata!')
        return cleaned_data

# form di registrazione
class SignUpForm(forms.Form):
    username = forms.CharField(label='username', max_length=50, widget=forms.TextInput(attrs={'class': 'field'}))
    email = forms.CharField(label='email', max_length=50, widget=forms.TextInput(attrs={'class': 'field'}))
    password = forms.CharField(label='password', max_length=50, widget=forms.PasswordInput(attrs={'class': 'field'}))
    confirm = forms.CharField(label='conferma password', max_length=50,
                              widget=forms.PasswordInput(attrs={'class': 'field'}))

    def clean(self):# restitusce errore se l userneme o l email esistono gia o se password e conferma sono diverse
        cleaned_data = super(SignUpForm, self).clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm')
        checkEmail = User.objects.filter(email=email)
        checkUsername = User.objects.filter(username=username)

        if checkUsername.exists():
            self.add_error('username', '*utente esistente con questo username')
        if checkEmail.exists():
            self.add_error('email', '*email gia assocciata a un account')
        if confirm != password:
            self.add_error('confirm', '*inserire la stessa password')
        return cleaned_data

"""
    - FORM DASHBOARD -    
"""
# form aggiungi board
class AddBoardForm(forms.Form):
    boardname = forms.CharField(label='Nome board', max_length=50, widget=forms.TextInput(attrs={'class': 'field'}))

    def setUser(self, user):# funzione utilizzata per settare l utente loggata ed efetuare tutti i controlli necessari nel form
        self.userLoged = user

    def clean(self):# restitusce errore se esiste gia una board con quel nome
        cleaned_data = super(AddBoardForm, self).clean()
        boardname = cleaned_data.get('boardname')
        checkBoard = Board.objects.filter(name=boardname, users=self.userLoged)
        if checkBoard.exists():
            raise forms.ValidationError('*questo nome e gia utilizzato da un altra board')
        return cleaned_data

"""
    - FORM SCRUMBOARD -
"""
# form aggiungi colonna alla board
class AddColumnForm(forms.Form):
    boardId = forms.CharField(widget=forms.HiddenInput(), label='', required=False, empty_value=None)
    columnname = forms.CharField(label='Nome colonna', max_length=50, widget=forms.TextInput(attrs={'class': 'field'}))

    def setUser(self, user):# funzione utilizzata per settare l utente loggata ed efetuare tutti i controlli necessari nel form
        self.userLoged = user

    def clean(self):# restituisce errore se esiste una colonna con quel nome opure un errore ingestibile intercettato dalla view che restetuira not found
        cleaned_data = super(AddColumnForm, self).clean()
        columnname = cleaned_data.get('columnname')
        boardId = cleaned_data.get('boardId')
        if boardId is not None:
            checkBoard = Board.objects.filter(pk=boardId, users=self.userLoged)
            checkColumn = Column.objects.filter(name=columnname, board=checkBoard)
            if not checkBoard.exists():
                raise forms.ValidationError('*not_found')# errore ingestibile
            elif checkBoard.exists() and checkColumn.exists():
                self.add_error('columnname', '*questo nome e gia utilizzato da un altra colonna nella board')
        else:
            raise forms.ValidationError('*not_found')
        return cleaned_data

#form cancella colonna
class FormDeleteColumn(forms.Form):
    boardId = forms.CharField(widget=forms.HiddenInput(), label='')
    columnId = forms.CharField(widget=forms.HiddenInput(), label='')

    def setUser(self, user):# funzione utilizzata per settare l utente loggata ed efetuare tutti i controlli necessari nel form
        self.userLoged = user

    def clean(self):# restituisce un errore ingestibile se non esiste o non si ha accesso a tale colonna
        cleaned_data = super(FormDeleteColumn, self).clean()
        boardId = cleaned_data.get('boardId')
        columnId = cleaned_data.get('columnId')
        checkBoard = Board.objects.filter(pk=boardId, users=self.userLoged)
        checkColumn = Column.objects.filter(pk=columnId, board=boardId)
        if not checkBoard.exists() or not checkColumn.exists():
            raise forms.ValidationError('*not_found')# errore ingestibile
        return cleaned_data

# form aggiungi utente alla board
class AddUserToBoardForm(forms.Form):
    boardId = forms.CharField(widget=forms.HiddenInput(), label='')
    userId = forms.CharField(widget=forms.HiddenInput(), label='')

    def setUser(self, user):# funzione utilizzata per settare l utente loggata ed efetuare tutti i controlli necessari nel form
        self.userLoged = user

    def clean(self):# restitusce errore ingestibile se non esiste tale utente o board
        cleaned_data = super(AddUserToBoardForm, self).clean()
        boardId = cleaned_data.get('boardId')
        userId = cleaned_data.get('userId')
        checkBoard = Board.objects.filter(pk=boardId, users=self.userLoged)
        checkUser = User.objects.filter(pk=userId)
        if not checkBoard.exists() or userId is self.userLoged.pk or not checkUser.exists():
            raise forms.ValidationError('*not_found')# errore ingestibile
        return cleaned_data

"""
    - FORM COLONNA -
"""
# form modifica nome colonna
class FormModifyColumnName(forms.Form):
    boardId = forms.CharField(widget=forms.HiddenInput(), label='')
    columnId = forms.CharField(widget=forms.HiddenInput(), label='')
    newName = forms.CharField(label='Nome colonna', max_length=50, widget=forms.TextInput(attrs={'class': 'field',
                                                                                                 'disabled': 'true'}))
    checkbox = BooleanField(label='', required=False,
                            widget=forms.CheckboxInput(attrs={'name': 'onoffswitch',
                                                              'class': 'onoffswitch-checkbox',
                                                              'id': 'myonoffswitch',
                                                              'onclick': MODIFY_ACTIVATE_COLUMN}))

    def setUser(self, user):# funzione utilizzata per settare l utente loggata ed efetuare tutti i controlli necessari nel form
        self.userLoged = user

    def clean(self):#restituisce errore se il nome e gia utilizzato o u errore ingestibile nel caso in cui i dati hidden non sono coerenti
        cleaned_data = super(FormModifyColumnName, self).clean()
        boardId = cleaned_data.get('boardId')
        columnId = cleaned_data.get('columnId')
        newName = cleaned_data.get('newName')
        checkBoard = Board.objects.filter(pk=boardId, users=self.userLoged)
        checkColumn = Column.objects.filter(pk=columnId, board=boardId)
        if not checkBoard.exists() or not checkColumn.exists():
            raise forms.ValidationError('*not_found')# errore ingestibile
        elif checkBoard.exists() and checkColumn.exists() and \
                Column.objects.filter(name=newName, board=boardId).exclude(pk=columnId).exists():
            self.add_error('newName', '*questo nome e gia utilizzato')
        return cleaned_data

# form elimina card
class FormDeleteCard(forms.Form):
    boardId = forms.CharField(widget=forms.HiddenInput(), label='')
    columnId = forms.CharField(widget=forms.HiddenInput(), label='')
    cardId = forms.CharField(widget=forms.HiddenInput(), label='')

    def setUser(self, user):# funzione utilizzata per settare l'utente loggata ed efetuare tutti i controlli necessari nel form
        self.userLoged = user

    def clean(self):#restituisce errore se i dati hidden non sono coerenti
        cleaned_data = super(FormDeleteCard, self).clean()
        boardId = cleaned_data.get('boardId')
        columnId = cleaned_data.get('columnId')
        cardId = cleaned_data.get('cardId')
        checkBoard = Board.objects.filter(pk=boardId, users=self.userLoged)
        checkColumn = Column.objects.filter(pk=columnId, board=boardId)
        checkCard = Card.objects.filter(pk=cardId, column=columnId)
        if not checkBoard.exists() or not checkColumn.exists() or not checkCard.exists():
            raise forms.ValidationError('*not_found')# errore ingestibile
        return cleaned_data

"""
    - VISTE CARD -
"""
# form modifica card
class FormModifyCard(forms.Form):
    boardId = forms.CharField(widget=forms.HiddenInput(), label='')
    columnId = forms.CharField(widget=forms.HiddenInput(), label='')
    cardId = forms.CharField(widget=forms.HiddenInput(), label='')
    newColumn = forms.CharField(label='nome Colonna', max_length=50, widget=forms.TextInput(attrs={'class': 'field', 'disabled': 'true'}))
    newTitle = forms.CharField(label='titolo', max_length=50, widget=forms.TextInput(attrs={'class': 'field', 'disabled': 'true'}))
    newdescription = forms.CharField(widget=forms.Textarea(attrs={'class': 'field', 'disabled': 'true'}), label='descrizione')
    newDateExpired = forms.CharField(label='data di scadenza', widget=forms.DateInput(attrs={'id': 'datepicker', 'class': 'field', 'disabled': 'true'}))
    newStoryPoints = forms.IntegerField(label='Story Points', widget=forms.NumberInput(attrs={'class': 'field', 'disabled': 'true'}))
    checkbox = BooleanField(label='', required=False,
                            widget=forms.CheckboxInput(attrs={'name': 'onoffswitch',
                                                              'class': 'onoffswitch-checkbox',
                                                              'id': 'myonoffswitch',
                                                              'onclick': MODIFY_ACTIVATE_CARD}))

    def setUser(self, user):# funzione utilizzata per settare l utente loggata ed efetuare tutti i controlli necessari nel form
        self.userLoged = user

    def clean(self):# restituisce errore se il titolo e gia usato nella colonna se il nome nuova colonna non esiste se Storypoints sono minori uguali a 0
        cleaned_data = super(FormModifyCard, self).clean()
        boardId = cleaned_data.get('boardId')
        columnId = cleaned_data.get('columnId')
        cardId = cleaned_data.get('cardId')
        newColumn = cleaned_data.get('newColumn')
        newTitle = cleaned_data.get('newTitle')
        newStoryPoints = cleaned_data.get('newStoryPoints')
        checkBoard = Board.objects.filter(pk=boardId, users=self.userLoged)
        checkColumn = Column.objects.filter(pk=columnId, board=boardId)
        checkCard = Card.objects.filter(pk=cardId, column=columnId)
        checkColumnMove = Column.objects.filter(name=newColumn, board=boardId)

        if not checkBoard.exists() or not checkColumn.exists() or not checkCard.exists():
            raise forms.ValidationError('*not_found')# errore ingestibile
        elif checkBoard.exists() and checkColumn.exists() and checkCard.exists() and checkColumnMove.exists() and\
                Card.objects.filter(title=newTitle, column=checkColumnMove).exclude(pk=cardId).exists():
            self.add_error('newTitle', '*questo nome e gia utilizzato nella colonna di destinazione')
        if newStoryPoints <= 0:
            self.add_error('newStoryPoints', '*inserire un numero maggiore di  0')
        if not checkColumnMove.exists():
            self.add_error('newColumn', '*questa colonna non esiste')
        return cleaned_data

# forma aggiungi/rimuovi utente board alla card
class FormAddOrRemUserCard(forms.Form):
    boardId = forms.CharField(widget=forms.HiddenInput(), label='')
    columnId = forms.CharField(widget=forms.HiddenInput(), label='')
    cardId = forms.CharField(widget=forms.HiddenInput(), label='')
    userId = forms.CharField(widget=forms.HiddenInput(), label='')

    def setUser(self, user):# funzione utilizzata per settare l utente loggata ed efetuare tutti i controlli necessari nel form
        self.userLoged = user

    def clean(self): # restituisce errore ingestibile se dati hidden non sono coerenti
        cleaned_data = super(FormAddOrRemUserCard, self).clean()
        boardId = cleaned_data.get('boardId')
        columnId = cleaned_data.get('columnId')
        cardId = cleaned_data.get('cardId')
        userId = cleaned_data.get('userId')

        checkUser = User.objects.filter(pk=userId)
        checkBoardLoged = Board.objects.filter(pk=boardId, users=self.userLoged)
        checkColumn = Column.objects.filter(pk=columnId, board=boardId)
        checkCard = Card.objects.filter(pk=cardId, column=columnId)
        checkBoardAdded = Board.objects.filter(pk=boardId, users=self.userLoged)
        if not checkUser.exists() or not checkBoardLoged.exists() or not checkBoardAdded.exists()\
                or not checkColumn.exists() or not checkCard.exists():
            raise forms.ValidationError('*not_found')# errore ingestibile
        return cleaned_data

 #form crea card
class AddCardForm(forms.Form):
    next = forms.CharField(widget=forms.HiddenInput(), label='', required=False, empty_value=None)
    boardId = forms.CharField(widget=forms.HiddenInput(), label='', required=False, empty_value=None)
    columnId = forms.CharField(widget=forms.HiddenInput(), label='', required=False, empty_value=None)
    title = forms.CharField(label='titolo', max_length=50, widget=forms.TextInput(attrs={'class': 'field'}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'field'}), label='descrizione')
    dateExpired = forms.CharField(label='data di scadenza',
                                  widget=forms.DateInput(attrs={'id': 'datepicker', 'class': 'field'}))
    storyPoints = forms.IntegerField(label='Story Points', widget=forms.NumberInput(attrs={'class': 'field'}))

    def setUser(self, user):# funzione utilizzata per settare l utente loggata ed efetuare tutti i controlli necessari nel form
        self.userLoged = user

    def clean(self):# restitusce errore se la card esiste gia o li story poins sono minori uguali a zero
        cleaned_data = super(AddCardForm, self).clean()
        boardId = cleaned_data.get('boardId')
        columnId = cleaned_data.get('columnId')
        title = cleaned_data.get('title')
        next = cleaned_data.get('next')
        storyPoints = cleaned_data.get('storyPoints')
        if boardId is not None and columnId is not None and (next == 'scrumboard' or next == 'column'):
            checkBoard = Board.objects.filter(pk=boardId, users=self.userLoged)
            checkColumn = Column.objects.filter(pk=columnId, board=checkBoard)
            checkCard = Card.objects.filter(title=title, column=checkColumn)
            if not checkBoard.exists() or not checkColumn.exists():
                raise forms.ValidationError('*not_found')# errore ingestibile
            elif checkBoard.exists() and checkColumn.exists() and checkCard.exists():
                self.add_error('title', '*questa card e gia esistente')
            if storyPoints <= 0:
                self.add_error('storyPoints', '*inserire un numero maggiore 0')

        else:
            raise forms.ValidationError('*not_found')# errore ingestibile
        return cleaned_data


