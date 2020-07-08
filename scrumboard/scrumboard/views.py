import datetime
from django import forms
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models.aggregates import Sum, Count
from django.http import *
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from forms import SignInForm, SignUpForm, AddBoardForm, AddUserToBoardForm, AddColumnForm, AddCardForm, FormDeleteCard, \
    FormModifyColumnName, FormDeleteColumn, FormModifyCard, FormAddOrRemUserCard
from models import Board, Column, Card
from costant.costants import MODIFY_ACTIVATE_COLUMN, MODIFY_ACTIVATE_CARD, NOT_FOUND_PAGE

"""
    - VISTE GESTIONE ACCOUNT -   
"""
# vista di login richiede inserimento username e password se non esiste l utente o la password e sbagliata restituisce
#un errore
@require_http_methods(['GET', 'POST'])
def signInView(request):
    if request.user.is_authenticated: # se l'utente dispone gia di una sessione ridirigilo alla dashboard
        return redirect('dashboard')
    elif request.method == 'POST': # se il metodo e POST  e il form valido avvia la sessione utente e ridirigilo a next
        form = SignInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect(request.POST.get('next')) # next parametro contiene url pagina successiva
    else:  # se la richiesta e una GET publica Form vuoto
        form = SignInForm(initial={'next': request.GET.get('next', 'dashboard'), 'username': '', 'password': ''})
    return render(request, 'signin.html', {'form': form})

# vista registrazione richiede inserimento username email password e conferma password
# restituisce errore se esiste un altro utente con stesso username o stessa mail o se password e conferma non sono uguali
@require_http_methods(['GET', 'POST'])
def signUpView(request):
    if request.user.is_authenticated: # se l utente dispone gia di una sessione ridirigi alla dashboard
        return redirect('dashboard')
    elif request.method == 'POST': # se la richiesta e post e il form e valido registra l'utente e ridirigi a sign-in
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            User.objects.create_user(username=username, email=email, password=password)
            return redirect('sign-in')
    else:  # se la richiesta e una GET publica Form vuoto
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

#vista logout
@require_http_methods(['GET'])
@login_required(login_url='sign-in')
def signOutView(request):
    logout(request)
    return redirect('sign-in')

"""
    - VISTE DASHBOARD -    
"""
# vista dashbord in cui sono presenti tutte le board dell'utente
@require_http_methods(['GET'])
@login_required(login_url='sign-in')
def dashBoardView(request):
    boards = Board.objects.filter(users=request.user)
    return render(request, 'dashboard.html', {
        'boards': boards
    })

# vista burndown contiene il numero card della board, il numero di card scadute, il numero di StoryPoints utilizzati
# e il numero di card per ogni colonna
@require_http_methods(['GET'])
@login_required(login_url='sign-in')
def burndownView(request, boardId):
    if request.method == 'GET' and boardId is not None: # se il metodo e get e non esiste la board restituisce not found
        board = Board.objects.filter(pk=boardId, users=request.user)
        if not board.exists():
            return HttpResponseNotFound(NOT_FOUND_PAGE)
    column = Column.objects.filter(board=board)
    cardNum = Card.objects.filter(column__pk__in=column).count() # numero di card
    cardExpire = Card.objects.filter(column__pk__in=column, dateExpire__lt=datetime.datetime.now()).count()# numero di card scadute
    numStoryPoints = Card.objects.filter(column__pk__in=column).aggregate(Sum('storyPoints'))['storyPoints__sum'] #numero storypoints utilizzati
    numCardColumn = Card.objects.filter(column__pk__in=column).values('column').annotate(Count('title'))#numero carte per colonna
    #asseblaggio numero card colonna con rispettivo nome
    numCardColumn = [{'columnname': Column.objects.get(pk=elem['column']).name, 'num': elem['title__count']} for elem in numCardColumn]
    #unione con le colonne che anno zero card
    numCardColumn.extend([{'columnname': elem.name, 'num': 0} for elem in column if not Card.objects.filter(column=elem).exists()])
    return render(request, 'burndown.html', {
        'board': Board.objects.get(pk=boardId),
        'cardNum': cardNum,
        'numCardColumn': numCardColumn,
        'cardExpire': cardExpire,
        'numStoryPoints': numStoryPoints,
    })

#vista add board pagina raggiungibile dalla dashboard  serve ad aggiungere nuove board richiede l inserimento di un nome
# se esiste un altra board con il nome inserito restituisce un errore
@require_http_methods(['GET', 'POST'])
@login_required(login_url='sign-in')
def addBoardView(request):
    if request.method == 'POST': # se la richiesta e una POST e il form e valido aggiungi board
        user = User.objects.get(username=request.user.username)
        form = AddBoardForm(request.POST)
        form.setUser(user)
        if form.is_valid():
            boardname = form.cleaned_data.get('boardname')
            newBoard = Board(name=boardname)
            newBoard.save()
            newBoard.users.add(user)
            return redirect(newBoard.get_absolute_url())
    else: # se la richiesta e una GET publica Form vuoto
        form = AddBoardForm()
    return render(request, 'addboard.html', {'form': form})

"""
    - VISTE SCRUMBOARD -
"""
#  vista scrumboard in cui son presenti le colonne
#  della board con all'interno le proprie cards, la vista implementa inoltre la funzione di eliminazione colonna
@require_http_methods(['GET', 'POST'])
@login_required(login_url='sign-in')
def scrumBoardView(request, boardId=None):
    if request.method == 'GET' and boardId is not None:#se il metodo e una get e il boardId e sbagliato ritorna un not found
        board = Board.objects.filter(pk=boardId, users=request.user)
        if not board.exists():
            return HttpResponseNotFound(NOT_FOUND_PAGE)
    elif request.method == 'POST': # se il metodo e una post e il form e valido elimina la colonna
        userLoged = User.objects.get(username=request.user.username)
        form = FormDeleteColumn(request.POST)
        form.setUser(userLoged)
        if form.is_valid():
            columnId = form.cleaned_data.get('columnId')
            boardId = form.cleaned_data.get('boardId')
            Column.objects.get(pk=columnId).delete()
            return redirect(Board.objects.get(pk=boardId).get_absolute_url())
        else:
            return HttpResponseNotFound(NOT_FOUND_PAGE)
    else:
        return HttpResponseNotFound(NOT_FOUND_PAGE)
    queryColumn = Column.objects.filter(board=boardId)  # colonne della board
    column = []
    for elem in queryColumn: # costruzione elementi colonna contenenti card e form eliminazione
        auxCards = Card.objects.filter(column=elem)
        formDeleteColumn = FormDeleteColumn(initial={'boardId': elem.board.pk, 'columnId': elem.pk})
        cardsClass = {'column': elem, 'cards': auxCards, 'formDelete': formDeleteColumn}
        column.append(cardsClass)
    return render(request, 'scrumboard.html', {
        'columns_data': column,
        'board': Board.objects.get(pk=boardId),
    })

# vista aggiungi colonna ragiungibile dalla vista scrumboard richiede inserimento del nome della colonna
# se esiste un altra colonna con lo stesso nome restituisce errore
@require_http_methods(['GET', 'POST'])
@login_required(login_url='sign-in')
def addColumnView(request, boardId=None):
    if request.method == 'GET' and boardId is not None: # se il metodo e una GET e il board id non e di proprieta del user ritorna un notfound
        board = Board.objects.filter(pk=boardId, users=request.user)
        if not board.exists():
            return HttpResponseNotFound(NOT_FOUND_PAGE)
        form = AddColumnForm(initial={'boardId': boardId, 'name': ''})# preinserimento del board id nel form in un campo hidden
    elif request.method == 'POST':# se la richista e una post e il form e valido  crea una nuova colonna
        user = User.objects.get(username=request.user.username)
        form = AddColumnForm(request.POST)
        form.setUser(user)
        if form.is_valid():
            columnName = form.cleaned_data.get('columnname')
            boardId = form.cleaned_data.get('boardId')
            board = Board.objects.filter(users=request.user)
            newcolumn = Column(name=columnName, board=board.get(pk=boardId))
            newcolumn.save()
            return redirect(board.get(pk=boardId).get_absolute_url())
        elif '*not_found' in str(form.errors): # se tra gli errori del form e presente un not_found error restituisce la rispettiva pagina
            return HttpResponseNotFound(NOT_FOUND_PAGE)
        else:
            boardId = form.cleaned_data.get('boardId')
    else:
        return HttpResponseNotFound(NOT_FOUND_PAGE)
    return render(request, 'addcolumn.html', {'form': form,
                                              'board': Board.objects.get(pk=boardId)})

# vista aggiungi utenti alla board ragiungibile da scrumboard
#  visualizza gli utenti registrati nel sistema e quelli della board se parte della board l utente e eliminabile altrimenti
#e aggiungibile
@require_http_methods(['GET', 'POST'])
@login_required(login_url='sign-in')
def addUserToBoardView(request, boardId=None):
    if request.method == 'GET' and boardId is not None:# se la richiesta e una GET e il boardId non e deluser restitusce un notfound
        board = Board.objects.filter(pk=boardId, users=request.user)
        if not board.exists():
            return HttpResponseNotFound(NOT_FOUND_PAGE)
    elif request.method == 'POST':# se la richiesta e una post e il form e valido aggiunge o elimina l utente
        userLoged = User.objects.get(username=request.user.username)
        form = AddUserToBoardForm(request.POST)
        form.setUser(userLoged)
        if form.is_valid():
            boardId = form.cleaned_data.get('boardId')
            userId = form.cleaned_data.get('userId')
            userAdded = User.objects.get(pk=userId)
            if not Board.objects.filter(users=userAdded, pk=boardId).exists(): #se l utente non fa parte della board viene agiunto
                Board.objects.get(pk=boardId).users.add(userAdded)
            else:   # se l utente fa parte della board viene eliminato
                Board.objects.get(pk=boardId).users.remove(userAdded)
                board = Board.objects.filter(pk=boardId)
                column = Column.objects.filter(board=board)
                cards = Card.objects.filter(column__pk__in=column)
                for card in cards: # se l utente viene eliminato perde tutte le card della board a cui stava lavorando
                    if card.users.filter(username=userAdded).exists():
                        card.users.remove(userAdded)

            return redirect(Board.objects.get(pk=boardId).get_addUserToBoard_url())
        else:
            return HttpResponseNotFound(NOT_FOUND_PAGE)
    else:
        return HttpResponseNotFound(NOT_FOUND_PAGE)
    formListAdd = []
    formListDel = []
    for user in User.objects.all().exclude(username=request.user.username):#costruzione elemento utente contenente username email e form
        form = AddUserToBoardForm(initial={'boardId': boardId, 'userId': user.pk})  # form contenete dati hidden per eliminare aggiungere utente
        dict = {'user': user,
                'form': form}
        if Board.objects.filter(users=user, pk=boardId).exists():
            formListDel.append(dict)
        else:
            formListAdd.append(dict)
    return render(request, 'add_user_to_board.html', {'board': Board.objects.get(pk=boardId),
                                                      'formListAdd': formListAdd,
                                                      'formListDel': formListDel,
                                                      })

"""
    - VISTE COLONNA -
"""
#vista colonna permette la visualizzazione del nome e delle card in essa presenti
#inoltre implementa le funzionalita di cancellazione di una card e la modifica del nome se il nome esiste gia nella board ritorna errore
@require_http_methods(['GET', 'POST'])
@login_required(login_url='sign-in')
def columnView(request, boardId=None, columnId=None):
    errorsExceptStyle = False # dato utilizzato nel template per rendere attivo il bottone al suseguirsi di un errore nell'inserimento
    if request.method == 'GET' and boardId is not None and columnId is not None: # se il metodo e GET e la colonna non esiste ritorna not found
        column = Column.objects.filter(pk=columnId, board=boardId)
        board = Board.objects.filter(pk=boardId, users=request.user)
        if not board.exists() or not column.exists():
            return HttpResponseNotFound(NOT_FOUND_PAGE)
        formModifyColumn = FormModifyColumnName(initial={'boardId': boardId, 'columnId': columnId, # inizializza form per la modifica del nome
                                                         'newName': Column.objects.get(pk=columnId).name})
    elif request.method == 'POST': # se il metodo e post modifica nome colonna o elimina card
        userLoged = User.objects.get(username=request.user.username)
        formDeleteCard = FormDeleteCard(request.POST)
        formDeleteCard.setUser(userLoged)
        formModifyColumn = FormModifyColumnName(request.POST)
        formModifyColumn.setUser(userLoged)
        if formModifyColumn.is_valid(): # se il form di modifica e valido modifica nome
            columnId = formModifyColumn.cleaned_data.get('columnId')
            newName = formModifyColumn.cleaned_data.get('newName')
            column = Column.objects.get(pk=columnId)
            column.name = newName
            column.save()
            return redirect(Column.objects.get(pk=columnId).get_absolute_url())
        elif formDeleteCard.is_valid():# se il form di eliminazione e valido allora elimina card
            columnId = formDeleteCard.cleaned_data.get('columnId')
            cardId = formDeleteCard.cleaned_data.get('cardId')
            Card.objects.get(pk=cardId).delete()
            return redirect(Column.objects.get(pk=columnId).get_absolute_url())
        elif '*not_found' in str(formModifyColumn.errors) and '*not_found' not in str(formDeleteCard.errors):
            boardId = formDeleteCard.cleaned_data.get('boardId')
            columnId = formDeleteCard.cleaned_data.get('columnId')
        elif '*not_found' not in str(formModifyColumn.errors) and '*not_found' in str(formDeleteCard.errors):
            # se il form di modifica non e valido ma non ha errori not fount lascia il testo modificabile e il bottone attivo
            errorsExceptStyle = True
            boardId = formModifyColumn.cleaned_data.get('boardId')
            columnId = formModifyColumn.cleaned_data.get('columnId')
            formModifyColumn.fields['newName'].widget = forms.TextInput(attrs={'class': 'field'})
            formModifyColumn.fields['checkbox'].widget = forms.CheckboxInput(attrs={'name': 'onoffswitch',
                                                                                    'class': 'onoffswitch-checkbox',
                                                                                    'id': 'myonoffswitch',
                                                                                    'checked': 'true',
                                                                                    'onclick': MODIFY_ACTIVATE_COLUMN})
        else:
            return HttpResponseNotFound(NOT_FOUND_PAGE)
    else:
        return HttpResponseNotFound(NOT_FOUND_PAGE)
    queryCards = Card.objects.filter(column=columnId)
    cards = []
    for card in queryCards: # costruzione elementi card con dati e form di eliminazione
        formDelete = FormDeleteCard(initial={'boardId': boardId, 'columnId': columnId, 'cardId': card.pk})
        dict = {'card': card, 'formDelete': formDelete}
        cards.append(dict)
    return render(request, 'columndetail.html', {
        'board': Board.objects.get(pk=boardId),
        'column': Column.objects.get(pk=columnId),
        'cards': cards,
        'formModify': formModifyColumn,
        'errorsexcept': errorsExceptStyle,
    })

"""
    - VISTE CARD -
"""
#vista card view permette l agiunta o l'eliminazione degli utenti della board alla card
# permette di modifificare i dati della card
# permette di cambiare colonna atraverso il nome di essa
@require_http_methods(['GET', 'POST'])
@login_required(login_url='sign-in')
def cardsView(request, boardId=None, columnId=None, cardId=None):
    errorsExceptStyle = False # flag lascia attivo bottone a seguito di un errore
    if request.method == 'GET' and boardId is not None and columnId is not None and cardId is not None:
        board = Board.objects.filter(pk=boardId, users=request.user) # se la richiesta e get e non esiste la colonna ritorna notfound
        column = Column.objects.filter(pk=columnId, board=boardId)
        card = Card.objects.filter(pk=cardId, column=columnId)
        if not board.exists() or not column.exists() or not card.exists():
            return HttpResponseNotFound(NOT_FOUND_PAGE)
        # inizializza form con i dati della card
        formModifyCard = FormModifyCard(initial={'boardId':boardId, 'columnId':columnId, 'cardId':cardId,
                                                 'newColumn': column.get(pk=columnId).name, 'newTitle': card.get(pk=cardId).title,
                                                 'newdescription': card.get(pk=cardId).description, 'newDateExpired': card.get(pk=cardId).dateExpire,
                                                 'newStoryPoints': card.get(pk=cardId).storyPoints})
    elif request.method == 'POST': # se la richiesta e post modifica dati card o elimina/aggiungi utente board alla card
        userLoged = User.objects.get(username=request.user.username)
        formModifyCard = FormModifyCard(request.POST)
        formModifyCard.setUser(userLoged)
        formAddOrRemoveUser = FormAddOrRemUserCard(request.POST)
        formAddOrRemoveUser.setUser(userLoged)
        if formModifyCard.is_valid():# se il form di modifica e valido  allora modifica dati card
            cardId = formModifyCard.cleaned_data.get('cardId')
            newColumn = formModifyCard.cleaned_data.get('newColumn')
            newTitle = formModifyCard.cleaned_data.get('newTitle')
            newdescription = formModifyCard.cleaned_data.get('newdescription')
            newDateExpired = formModifyCard.cleaned_data.get('newDateExpired')
            newStoryPoints = formModifyCard.cleaned_data.get('newStoryPoints')
            card = Card.objects.get(pk=cardId)
            card.title = newTitle
            card.description = newdescription
            card.dateExpire = newDateExpired
            card.storyPoints = newStoryPoints
            card.column = Column.objects.get(name=newColumn)
            card.save()
            return redirect(Card.objects.get(pk=cardId).get_absolute_url())
        elif formAddOrRemoveUser.is_valid():# se il form aggiungi utente e valido allora elimina o agginugi utente
            cardId = formAddOrRemoveUser.cleaned_data.get('cardId')
            userId = formAddOrRemoveUser.cleaned_data.get('userId')
            userAdded = User.objects.get(pk=userId)
            if not Card.objects.filter(users=userAdded, pk=cardId).exists():# se l utente non fa parte  della card aggiungilo
                Card.objects.get(pk=cardId).users.add(userAdded)
            else: # se l utente fa parte della card eliminalo
                Card.objects.get(pk=cardId).users.remove(userAdded)
            return redirect(Card.objects.get(pk=cardId).get_absolute_url())
        elif '*not_found' in str(formModifyCard.errors) and '*not_found' not in str(formAddOrRemoveUser.errors):
            boardId = formAddOrRemoveUser.cleaned_data.get('boardId')
            columnId = formAddOrRemoveUser.cleaned_data.get('columnId')
            cardId = formAddOrRemoveUser.cleaned_data.get('cardId')

        elif '*not_found' not in str(formModifyCard.errors) and '*not_found' in str(formAddOrRemoveUser.errors):
            errorsExceptStyle = True # se l errore proviene da modifiy card ma non e un notfund lascia il testo modificabile all'utente
            boardId = formModifyCard.cleaned_data.get('boardId')
            columnId = formModifyCard.cleaned_data.get('columnId')
            cardId = formModifyCard.cleaned_data.get('cardId')
            formModifyCard.fields['newTitle'].widget = forms.TextInput(attrs={'class': 'field'})
            formModifyCard.fields['newColumn'].widget = forms.TextInput(attrs={'class': 'field'})
            formModifyCard.fields['newdescription'].widget = forms.Textarea(attrs={'class': 'field'})
            formModifyCard.fields['newDateExpired'].widget = forms.DateInput(attrs={'id': 'datepicker', 'class': 'field'})
            formModifyCard.fields['newStoryPoints'].widget = forms.NumberInput(attrs={'class': 'field'})
            formModifyCard.fields['checkbox'].widget = forms.CheckboxInput(attrs={'name': 'onoffswitch',
                                                                                    'class': 'onoffswitch-checkbox',
                                                                                    'id': 'myonoffswitch',
                                                                                    'checked': 'true',
                                                                                    'onclick': MODIFY_ACTIVATE_CARD})
        else:
            return HttpResponseNotFound(NOT_FOUND_PAGE)
    else:
        return HttpResponseNotFound(NOT_FOUND_PAGE)
    formListAdd = []
    formListDel = []
    for user in User.objects.all():# creazione struttura utenti contenente dati e form agiung/elimina utente
        form = FormAddOrRemUserCard(initial={'boardId': boardId, 'columnId': columnId, 'cardId': cardId, 'userId': user.pk})
        dict = {'user': user,
                'form': form}
        if Board.objects.filter(pk=boardId, users=user).exists() and Card.objects.filter(users=user, pk=cardId).exists():
            formListDel.append(dict)
        elif Board.objects.filter(pk=boardId, users=user).exists() and not Card.objects.filter(users=user, pk=cardId).exists():
            formListAdd.append(dict)
    return render(request, 'cardetail.html', {
            'board': Board.objects.get(pk=boardId),
            'column': Column.objects.get(pk=columnId),
            'card': Card.objects.get(pk=cardId),
            'formModify': formModifyCard,
            'formListDel': formListDel,
            'formListAdd': formListAdd,
            'errorsexcept': errorsExceptStyle
        })

# vista aggiungi card raggiungibile sia da scrumboard che da vista colonna grazie a un parametro next una volta agiunta la carta
# ritorna alla vista chiamante
# richede l iserimento dei dati della card se il titolo esiste gia restitusce errore, se lestory points sono minori o uguali a zero
# restituisce errore
@require_http_methods(['GET', 'POST'])
@login_required(login_url='sign-in')
def addCardView(request, boardId=None, columnId=None, next=None):
    if request.method == 'GET' and boardId is not None and columnId is not None:# se il metodo e un GET e non esiste la colonna ritorna not found
        board = Board.objects.filter(pk=boardId, users=request.user)
        column = Column.objects.filter(pk=columnId, board=board)
        if not board.exists() or not column.exists() or not (next == 'column' or next == 'scrumboard'):#a se next non proviene da colonna oscrumboard ritorna not found
            return HttpResponseNotFound(NOT_FOUND_PAGE)
        else:#altrimenti crea il form di compilazione per la card
            form = AddCardForm(initial={'boardId': boardId, 'columnId': columnId, 'next': next})
    elif request.method == 'POST':# se la richiesta e una POST  e il form e valido aggiungi una card
        user = User.objects.get(username=request.user.username)
        form = AddCardForm(request.POST)
        form.setUser(user)
        if form.is_valid():
            boardId = form.cleaned_data.get('boardId')
            columnId = form.cleaned_data.get('columnId')
            title = form.cleaned_data.get('title')
            description = form.cleaned_data.get('description')
            dateExpired = form.cleaned_data.get('dateExpired')
            storyPoints = form.cleaned_data.get('storyPoints')
            column = Column.objects.get(pk=columnId)
            Card.objects.create(title=title, description=description, dateExpire=dateExpired, storyPoints=storyPoints,
                                column=column)
            next = form.cleaned_data.get('next')
            if next == 'scrumboard':# se addcard e stata richiamata da scrumboard ritorna a scrumboard
                return redirect(reverse('scrum-board', args=[str(boardId)]))
            elif next == 'column':# se e stata chiamata da column ritorna a column
                return redirect(reverse('column', args=[str(boardId), str(columnId)]))
        elif '*not_found' in str(form.errors):
            return HttpResponseNotFound(NOT_FOUND_PAGE)
        else:
            boardId = form.cleaned_data.get('boardId')
            columnId = form.cleaned_data.get('columnId')
    else:
        return HttpResponseNotFound(NOT_FOUND_PAGE)
    returnColumn = False
    if next == 'column':# flag per il bottone template ritorna a colonna
        returnColumn = True
    return render(request, 'addcard.html', {'form': form,
                                            'column': Column.objects.get(pk=columnId),
                                            'board': Board.objects.get(pk=boardId),
                                            'retcolumn': returnColumn})




