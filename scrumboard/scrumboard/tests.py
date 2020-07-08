import datetime
import unittest

from django.db.models import Sum, Count
from django.test import TestCase, Client
from models import *
#  /*------------------------------------------------------------------------*/
#   * Progetto - Ingegneria del Software - tests.py
#  /*------------------------------------------------------------------------*/
#   * Nome:         - Scrumboard
#   * Descrizione:  - Applicazione Web per la gestione di una board scrum
#   * Autori:       - Pilloni Raffaele  - 65151
#                   - Meloni Giacomo    - 65181
#                   - Ziantoni Stefano  - 65197
#                   - Ibba Andrea       - 65258
#  /*------------------------------------------------------------------------*/

'''
    TEST DI ACCETTAZIONE SIGN-IN:
    - testSignIn_valido -> test per verificare il corretto accesso da parte dell'utente
    - testSignIn_vuoto -> test per verificare l'accesso senza inserire nessun parametro
    - testSignIn_non_valido -> test per verificare l'accesso inserendo credenziali errate
'''

class SignInTest(TestCase):
    '''
        Registrazione dell'utente per effettuare il test
    '''
    def setUp(self):
        self.client = Client()

        datiRegistrazione={
            'username': 'admin',
            'email': 'admin@mail.org',
            'password': 'pass',
            'confirm': 'pass'
        }
        # registrazione utente
        self.client.post(reverse('sign-up'), datiRegistrazione)

    #viene fatto un test di accesso riuscito inserendo le credenziali dell'utente registrato nel setUp
    def testSignIn_valido(self):
        self.dati = {
            'username': 'admin',
            'password': 'pass',
            'next': reverse('dashboard')
        }
        #richiesta di login con i dati di accesso e controllo se utente attivo
        response = self.client.post(reverse('sign-in'), self.dati, follow=True)
        self.assertTrue(response.context['user'].is_active)
        #richiesta GET per accedere alla dashboard controllo se l'utente puo accedere
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    #viene fatto un test di accesso negato non inserendo nessun dato
    def testSignIn_vuoto(self):
        self.credenzialiValide = {
            'username': '',
            'password': '',
            'next': reverse('dashboard')
        }
        #richiesta di login con i dati di accesso e controllo se utente attivo
        response = self.client.post(reverse('sign-in'), self.credenzialiValide, follow=True)
        self.assertFalse(response.context['user'].is_active)
        #richiesta GET per accedere alla dashboard controllo se l'utente puo accedere
        response = self.client.get(reverse('dashboard'))
        self.assertNotEqual(response.status_code, 200)

    #viene fatto un test di accesso negato non inserendo credenziali non valide
    def testSignIn_non_valido(self):
        self.credenzialiNonValide = {
            'username': 'paolo',
            'password': 'dekfurns',
            'next': reverse('dashboard')
        }
        #richiesta di login con i dati di accesso e controllo se utente attivo e se viene visualizzato il messaggio di errore
        response = self.client.post(reverse('sign-in'), self.credenzialiNonValide, follow=True)
        self.assertFalse(response.context['user'].is_active)
        self.assertContains(response, '*username o password errata!')
        #richiesta GET per accedere alla dashboard controllo se l'utente puo accedere
        response = self.client.get(reverse('dashboard'))
        self.assertNotEqual(response.status_code, 200)

'''
    TEST DI ACCETTAZIONE SIGN-UP:
    - testSignUp -> test di verifica di effettiva registrazione dell'utente e reindirizzamento alla pagina di login
    - testSignUp_errore_utente_esistente -> test di verifica messaggio di errore per utente gia esistente
    - testSignUp_errore_email_esistente -> test di verifica messaggio di errore per mail gia esistente
    - testSignUp_errore_email_user_esistenti -> test di verifica messaggi di errore multipli user e mail gia esistenti
    - testSignUp_errore_password_diversa -> test di verifica messaggi di errore password e conferma password non uguali
    - testSignUp_errore_user_email_pass -> test di verifica messaggi di errore user,mail e password (errori multipli)
'''

class SignUpTest(TestCase):
    '''
        Registrazione di un utente per poter effettuare tutti i test
    '''
    def setUp(self):
        self.client = Client()
        datiRegistrazione = {'username': 'userJustReg',
                'email': 'userJustReg@email.com',
                'password': '1234',
                'confirm': '1234'}
        # registrazione utente
        self.client.post(reverse('sign-up'), datiRegistrazione)

    #test di verifica di successivo reindirizzamento dopo la registrazione alla pagina di accesso
    def testSignUp(self):
        dati = {'username': 'userToReg',
                'email': 'userToReg@email.com',
                'password': '1234',
                'confirm': '1234'}

        # registrazione utente e controllo reindirizzamento a pagina di sign-in
        response = self.client.post(reverse('sign-up'), dati)
        self.assertEqual(response.url, reverse('sign-in'))
        #verifica effettiva creazione utente
        self.assertTrue(User.objects.filter(username= 'userToReg').exists())

    #test di verifica di errore per inserimento di un username gia presente
    def testSignUp_errore_utente_esistente(self):
        dati = {'username': 'userJustReg',
                'email': 'userToReg@email.com',
                'password': '1234',
                'confirm': '1234'}
        # registrazione utente e controllo messaggio d'errore
        response = self.client.post(reverse('sign-up'), dati)
        self.assertContains(response, '*utente esistente con questo username')
        self.assertFalse(User.objects.filter(email= 'userToReg@email.com').exists())

    #test di verifica di errore per email gia esistente
    def testSignUp_errore_email_esistente(self):
        dati = {'username': 'userToReg',
                'email': 'userJustReg@email.com',
                'password': '1234',
                'confirm': '1234'}
        # registrazione utente e controllo messaggio d'errore
        response = self.client.post(reverse('sign-up'), dati)
        self.assertContains(response, '*email gia assocciata a un account')

    # test di verifica di errore per email e utenti gia esistenti (errori multipli)
    def testSignUp_errore_email_user_esistenti(self):
        dati = {'username': 'userJustReg',
                'email': 'userJustReg@email.com',
                'password': '1234',
                'confirm': '1234'}
        # registrazione utente e controllo messaggio d'errore
        response = self.client.post(reverse('sign-up'), dati)
        self.assertContains(response, '*utente esistente con questo username')
        self.assertContains(response, '*email gia assocciata a un account')

    # test di verifica di errore password e conferma password sbagliate
    def testSignUp_errore_password_diversa(self):
        dati = {'username': 'userToReg',
                'email': 'userToReg@email.com',
                'password': '1234',
                'confirm': '12345'}
        # registrazione utente e controllo messaggio d'errore
        response = self.client.post(reverse('sign-up'), dati)
        self.assertContains(response, '*inserire la stessa password')

    # test di verifica di errore password e conferma password sbagliate, errore username e mail gia esistenti (errori multipli)
    def testSignUp_errore_user_email_pass(self):
        dati = {'username': 'userJustReg',
                'email': 'userJustReg@email.com',
                'password': '1234',
                'confirm': '12345'}
        # registrazione utente e controllo messaggio d'errore
        response = self.client.post(reverse('sign-up'), dati)
        self.assertContains(response, '*utente esistente con questo username')
        self.assertContains(response, '*email gia assocciata a un account')
        self.assertContains(response, '*inserire la stessa password')

'''
    TEST DI ACCETTAZIONE LOGOUT:
    - testLogOut -> test di verifica di avvenuta disconnessione dell'utente e reindirizzamento alla pagina di Sign-in
'''

class LogoutTest(TestCase):
    '''
        Registrazione e autenticazione di un utente per poter effettuare il test
    '''

    def setUp(self):
        self.client = Client()
        datiRegistrazione = {'username': 'userJustReg',
                             'email': 'userJustReg@email.com',
                             'password': '1234',
                             'confirm': '1234'}
        # registrazione utente
        self.client.post(reverse('sign-up'), datiRegistrazione)

        datiAccesso = {'username': 'userJustReg',
                       'password': '1234',
                       'next': 'dashboard'}
        # login utente
        response = self.client.post(reverse('sign-in'), datiAccesso, follow=True)
        self.user = response.context['user']

    #test di verifica effettivo reindirizzamento alla pagina di login
    def testLogOut(self):
        #chiamata di logout e controllo reindirizzamento
        response = self.client.get(reverse('sign-out'))
        self.assertEquals(response.url, reverse('sign-in'))

'''
    TEST DI ACCETTAZIONE AGGIUNTA BOARD:
    - testAddBoard -> test di verifica avvenuta creazione di una board
    - testAddBoard_errore -> test di verifica errore nella creazione di una board con un nome gia esistente
'''
class AddBoardTest (TestCase):
    '''
        Registrazione e autenticazione di un utente, successiva creazione di una board
        per effettuare i test
    '''

    def setUp(self):
        self.client = Client()
        datiRegistrazione = {'username': 'userJustReg',
                             'email': 'userJustReg@email.com',
                             'password': '1234',
                             'confirm': '1234'}
        # registrazione utente
        self.client.post(reverse('sign-up'), datiRegistrazione)

        datiAccesso = {'username': 'userJustReg',
                       'password': '1234',
                       'next': 'dashboard'}
        # login utente
        response = self.client.post(reverse('sign-in'), datiAccesso, follow=True)
        self.user = response.context['user']

        boardJustAdd = {'boardname': 'board'}
        # aggiunta board
        self.client.post(reverse('add-board'), boardJustAdd)

    #test di verifica avvenuta creazione della board
    def testAddBoard(self):
        boardToAdd = {'boardname': 'boardAggiunta'}
        #inserimento board e controllo se e stata inserita e se si puo raggiungere
        response = self.client.post(reverse('add-board'), boardToAdd)
        idBoardAggiunta = Board.objects.get(name='boardAggiunta').pk
        self.assertEquals(response.url, reverse('scrum-board', args=[idBoardAggiunta]))
        response = self.client.get(reverse('scrum-board', args=[idBoardAggiunta]))
        self.assertEquals(response.status_code, 200)

    #test di verifica messaggio di errore per nome board gia utilizzato
    def testAddBoard_errore(self):
        boardToAdd = {'boardname': 'board'}
        # richiesta di aggiunta board e controllo segnalazione errore
        response = self.client.post(reverse('add-board'), boardToAdd)
        self.assertContains(response, '*questo nome e gia utilizzato da un altra board')

'''
    TEST DI ACCETTAZIONE AGGIUNTA/ELIMINAZIONE COLONNA:
    - testAddColumn -> test di verifica avvenuta creazione di una colonna
    - testAddColumn_errore -> test di verifica errore nella creazione di una colonna con un nome gia esistente
    - testDeleteColumn -> test di verifica effettiva eliminazione di una colonna
'''
class Add_Delete_ColumnnTest (TestCase):
    '''
        Registrazione e autenticazione di un utente, successiva creazione di una board
        e di colonne associate alla board per effettuare i test
    '''

    def setUp(self):
        self.client = Client()
        datiRegistrazione = {'username': 'userJustReg',
                             'email': 'userJustReg@email.com',
                             'password': '1234',
                             'confirm': '1234'}
        # registrazione utente
        self.client.post(reverse('sign-up'), datiRegistrazione)

        datiAccesso = {'username': 'userJustReg',
                       'password': '1234',
                       'next': 'dashboard'}
        # login utente
        response = self.client.post(reverse('sign-in'), datiAccesso, follow=True)
        self.user = response.context['user']

        boardJustAdd = {'boardname': 'board'}
        # aggiunta board
        response = self.client.post(reverse('add-board'), boardJustAdd)

        idBoard = Board.objects.get(name='board').pk
        columnJustAdd1 = {'columnname': 'colonnAggiunta1', 'boardId': idBoard}
        columnJustAdd2 = {'columnname': 'colonnAggiunta2', 'boardId': idBoard}
        columnJustAdd3 = {'columnname': 'colonnAggiunta3', 'boardId': idBoard}

        # aggiunta colonne
        self.client.post(reverse('add-column-post'), columnJustAdd1)
        self.client.post(reverse('add-column-post'), columnJustAdd2)
        self.client.post(reverse('add-column-post'), columnJustAdd3)

    #test di verifica effettiva creazione della colonna
    def testAddColumn(self):
        idBoard = Board.objects.get(name='board').pk
        ColumnToAdd = {'columnname': 'colonnAggiunta', 'boardId': idBoard}

        #richiesta di aggiunta colonna e controllo reindirizzamento alla board di appartenenza
        response = self.client.post(reverse('add-column-post'), ColumnToAdd)
        self.assertEquals(response.url, reverse('scrum-board', args=[idBoard]))
        idColumn = Column.objects.get(name='colonnAggiunta').pk

        #richiesta di accesso alla colonna creata e controllo di accesso effettuato
        response = self.client.get(reverse('column', args=[idBoard, idColumn]))
        self.assertEqual(response.status_code, 200)

    # test di verifica messaggio di errore per inserimento nome colonna gia utilizzato
    def testAddColumn_errore(self):
        idBoard = Board.objects.get(name='board').pk
        ColumnToAdd = {'columnname': 'colonnAggiunta1', 'boardId': idBoard}

        #richiesta di aggiunta colonna e controllo errore
        response = self.client.post(reverse('add-column-post'), ColumnToAdd)
        self.assertContains(response, '*questo nome e gia utilizzato da un altra colonna nella board')

    # test di verifica effettiva creazione della colonna
    def testDeleteColumn(self):
        idBoard = Board.objects.get(name='board').pk
        idColumn = Column.objects.get(name='colonnAggiunta1').pk
        ColumnToDel = {'columnId': idColumn, 'boardId': idBoard}

        #richiesta di eliminazione colonna esistente e controllo su effettiva eliminazione
        response = self.client.post(reverse('del-column'), ColumnToDel)
        self.assertEquals(response.url, reverse('scrum-board', args=[idBoard]))
        response = self.client.get(reverse('column', args=[idBoard, idColumn]))
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 404)

'''
    TEST DI ACCETTAZIONE AGGIUNTA/ELIMINAZIONE CARD:
    - testAddCard_returnToColumnView -> test di verifica avvenuta creazione di una card e ritorno alla vista della colonna
    - testAddCard_returnToScrumboardView -> test di verifica avvenuta creazione di una card e ritorno alla vista della scrumboard
    - testAddCard_errore_title_esistente -> test di verifica errore per titolo card gia esistente in una card della stessa colonna 
    - testAddCard_errore_story_points -> test di verifica errore per inserimento story point con valori <= 0
    - testDeleteCard -> test di verifica effettiva rimozione di una card 
'''
class Add_Delete_CardTest (TestCase):
    '''
        Registrazione e autenticazione di un utente, successiva creazione di una board
        e di una colonna associate alla board, e di una card associata a tale colonna
        per effettuare i test
    '''

    def setUp(self):
        self.client = Client()
        datiRegistrazione = {'username': 'userJustReg',
                             'email': 'userJustReg@email.com',
                             'password': '1234',
                             'confirm': '1234'}
        # registrazione utente
        self.client.post(reverse('sign-up'), datiRegistrazione)

        datiAccesso = {'username': 'userJustReg',
                       'password': '1234',
                       'next': 'dashboard'}
        # login utente
        response = self.client.post(reverse('sign-in'), datiAccesso, follow=True)
        self.user = response.context['user']

        boardJustAdd = {'boardname': 'board'}
        #aggiunta board
        self.client.post(reverse('add-board'), boardJustAdd)

        idBoard = Board.objects.get(name='board').pk
        columnJustAdd1 = {'columnname': 'colonnAggiunta1', 'boardId': idBoard}
        #aggiunta colonna
        self.client.post(reverse('add-column-post'), columnJustAdd1)

        idColumn = Column.objects.get(name='colonnAggiunta1', board= idBoard).pk

        datiCardJustAdd1 = {'title': 'Card#1',
                            'description': 'descrizione#1',
                            'storyPoints': '2',
                            'dateExpired': '2018-02-15',
                            'next': 'scrumboard',
                            'boardId': idBoard,
                            'columnId': idColumn}
        #aggiunta card
        self.client.post(reverse('add-card-post'), datiCardJustAdd1)

    #test di verifica effettiva creazione della card con reindirizzamento alla vista colonna di riferimento una volta creata
    def testAddCard_returnToColumnView(self):
        idBoard = Board.objects.get(name='board').pk
        idColumn = Column.objects.get(name='colonnAggiunta1', board= idBoard).pk

        datiCardToAdd = {'title': 'Card#2',
                        'description': 'descrizione#2',
                        'storyPoints': '2',
                        'dateExpired': '2018-02-15',
                        'next': 'column',
                        'boardId': idBoard,
                        'columnId': idColumn}

        #richiesta aggiunta card e controllo effettiva creazione e reindirizzamento
        response = self.client.post(reverse('add-card-post'), datiCardToAdd)
        self.assertEquals(response.url, reverse('column', args=[idBoard, idColumn]))
        idCard = Card.objects.get(title='Card#2').pk
        response = self.client.get(reverse('card', args=[idBoard, idColumn, idCard]))
        self.assertEqual(response.status_code, 200)

    #test di verifica effettiva creazione della card con reindirizzamento alla vista della board al quale appartiene
    def testAddCard_returnToScrumboardView(self):
        idBoard = Board.objects.get(name='board').pk
        idColumn = Column.objects.get(name='colonnAggiunta1', board= idBoard).pk

        datiCardToAdd = {'title': 'Card#2',
                        'description': 'descrizione#2',
                        'storyPoints': '2',
                        'dateExpired': '2018-02-15',
                        'next': 'scrumboard',
                        'boardId': idBoard,
                        'columnId': idColumn}

        # richiesta aggiunta card e controllo effettiva creazione e reindirizzamento
        response = self.client.post(reverse('add-card-post'), datiCardToAdd)
        self.assertEquals(response.url, reverse('scrum-board', args=[idBoard]))
        idCard = Card.objects.get(title='Card#2').pk
        response = self.client.get(reverse('card', args=[idBoard, idColumn, idCard]))
        self.assertEqual(response.status_code, 200)

    #test di verifica di errore in caso di inserimento di titolo esistente in un altra card della stessa colonna
    def testAddCard_errore_title_esistente(self):
        idBoard = Board.objects.get(name='board').pk
        idColumn = Column.objects.get(name='colonnAggiunta1', board=idBoard).pk

        datiCardToAdd = {'title': 'Card#1',
                         'description': 'descrizione#2',
                         'storyPoints': '2',
                         'dateExpired': '2018-02-15',
                         'next': 'column',
                         'boardId': idBoard,
                         'columnId': idColumn}

        response = self.client.post(reverse('add-card-post'), datiCardToAdd)
        self.assertContains(response, '*questa card e gia esistente')

    #test di verifica di errore in caso di inserimento di story point <= 0
    def testAddCard_errore_story_points(self):
        idBoard = Board.objects.get(name='board').pk
        idColumn = Column.objects.get(name='colonnAggiunta1', board=idBoard).pk

        datiCardToAdd1 = {'title': 'Card#2',
                         'description': 'descrizione#2',
                         'storyPoints': '0',
                         'dateExpired': '2018-02-15',
                         'next': 'column',
                         'boardId': idBoard,
                         'columnId': idColumn}

        datiCardToAdd2 = {'title': 'Card#2',
                          'description': 'descrizione#2',
                          'storyPoints': '-25',
                          'dateExpired': '2018-02-15',
                          'next': 'column',
                          'boardId': idBoard,
                          'columnId': idColumn}

        response = self.client.post(reverse('add-card-post'), datiCardToAdd1)
        self.assertContains(response, '*inserire un numero maggiore 0')

        response = self.client.post(reverse('add-card-post'), datiCardToAdd2)
        self.assertContains(response, '*inserire un numero maggiore 0')

    #test per la verifica della effettiva eliminazione di una card
    def testDeleteCard(self):
        idBoard = Board.objects.get(name='board').pk
        idColumn = Column.objects.get(name='colonnAggiunta1').pk
        idCard = Card.objects.get(title='Card#1').pk

        #richiesta di eliminazione di una card esistente e controllo effettiva eliminazione
        CardToDel = {'cardId': idCard,'columnId': idColumn, 'boardId': idBoard}
        response = self.client.post(reverse('post-column'), CardToDel)
        self.assertEquals(response.url, reverse('column', args=[idBoard, idColumn]))
        response = self.client.get(reverse('card', args=[idBoard, idColumn, idCard]))
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 404)

'''
    TEST DI ACCETTAZIONE AGGIUNTA/ELIMINAZIONE UTENTE BOARD:
    - testAdd_Delete_UserToBoard -> test di verifica aggiunta e successiva eliminazione di un utente da una board
'''
class Add_Delete_UserToBoardTest (TestCase):
    '''
        Registrazione e autenticazione di due utenti, creazione di una board
        per poter effettuare i test
    '''

    def setUp(self):
        self.client = Client()
        datiUser1 = {'username': 'user1',
                     'email': 'user1@email.com',
                     'password': '1234',
                     'confirm': '1234'}

        datiUser2 = {'username': 'user2',
                     'email': 'user2@email.com',
                     'password': '1234',
                     'confirm': '1234'}
        # registrazione utenti
        self.client.post(reverse('sign-up'), datiUser1)
        self.client.post(reverse('sign-up'), datiUser2)

        datiAccessoUser1 = {'username': 'user1',
                            'password': '1234',
                            'next': 'dashboard'}

        datiAccessoUser2 = {'username': 'user2',
                            'password': '1234',
                            'next': 'dashboard'}
        #login utente
        self.client.post(reverse('sign-in'), datiAccessoUser1, follow=True)

        boardJustAdd = {'boardname': 'board'}
        #aggiunta board
        self.client.post(reverse('add-board'), boardJustAdd)
        #logout utente
        self.client.get(reverse('sign-out'))

    #test di verifica per il controllo dell'effettiva aggiunta o rimozione di un utente dalla board
    def testAdd_Delete_UserToBoard(self):
        idBoard = Board.objects.get(name='board').pk
        idUser1 = User.objects.get(username='user1').pk
        idUser2 = User.objects.get(username='user2').pk

        datiAccessoUser1 = {'username': 'user1',
                            'password': '1234',
                            'next': 'dashboard'}

        datiAccessoUser2 = {'username': 'user2',
                            'password': '1234',
                            'next': 'dashboard'}
        # accesso e tentativo di accesso alla board
        self.client.post(reverse('sign-in'), datiAccessoUser2, follow=True)
        response = self.client.get(reverse('scrum-board',args=[idBoard]))
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 404)
        # disconnessione utente 2 e login utente 1 e accesso alla sua board
        self.client.get(reverse('sign-out'))
        self.client.post(reverse('sign-in'), datiAccessoUser1, follow=True)
        response = self.client.get(reverse('scrum-board', args=[idBoard]))
        self.assertEqual(response.status_code, 200)

        datiUserToAdd = {'boardId':idBoard,
                         'userId': idUser2}
        #richiesta di aggiuta utente 2 alla board
        response = self.client.post(reverse('add-user-to-board-post'), datiUserToAdd)
        self.assertEquals(response.url, reverse('add-user-to-board', args=[idBoard]))

        # logout utente 1 e login utente 2 e accesso alla board
        self.client.get(reverse('sign-out'))
        self.client.post(reverse('sign-in'), datiAccessoUser1, follow=True)
        response = self.client.get(reverse('scrum-board', args=[idBoard]))
        self.assertEqual(response.status_code, 200)

        datiUserToDel = {'boardId': idBoard,
                         'userId': idUser1}
        #richiesta di eliminazione utente 1 dalla board
        response = self.client.post(reverse('add-user-to-board-post'), datiUserToDel)
        self.assertEquals(response.url, reverse('add-user-to-board', args=[idBoard]))

        # logout utente2 login utente1 e accesso negato alla board dal quale e stato eliminato
        self.client.get(reverse('sign-out'))
        self.client.post(reverse('sign-in'), datiAccessoUser1, follow=True)
        response = self.client.get(reverse('scrum-board', args=[idBoard]))
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 404)

'''
    TEST DI ACCETTAZIONE AGGIUNTA/ELIMINAZIONE UTENTE CARD:
    - testAdd_Delete_UserToBoard -> test di verifica aggiunta e successiva eliminazione di un utente da una board
'''
class Add_Delete_UserToCard (TestCase):
    '''
        Registrazione e autenticazione di due utenti, creazione di una board
        con all'interno tre colonne e inserimento di due card all'interno di una colonna
        per effettuare i test
    '''

    def setUp(self):
        self.client = Client()
        datiUser1 = {'username': 'user1',
                     'email': 'user1@email.com',
                     'password': '1234',
                     'confirm': '1234'}

        datiUser2 = {'username': 'user2',
                     'email': 'user2@email.com',
                     'password': '1234',
                     'confirm': '1234'}
        # registrazione utenti
        self.client.post(reverse('sign-up'), datiUser1)
        self.client.post(reverse('sign-up'), datiUser2)

        datiAccessoUser1 = {'username': 'user1',
                            'password': '1234',
                            'next': 'dashboard'}

        # login utente
        self.client.post(reverse('sign-in'), datiAccessoUser1, follow=True)

        boardJustAdd = {'boardname': 'board'}
        #aggiunta board
        self.client.post(reverse('add-board'), boardJustAdd)

        idBoard = Board.objects.get(name='board').pk
        columnJustAdd1 = {'columnname': 'colonnAggiunta1', 'boardId': idBoard}
        columnJustAdd2 = {'columnname': 'colonnAggiunta2', 'boardId': idBoard}
        columnJustAdd3 = {'columnname': 'colonnAggiunta3', 'boardId': idBoard}

        #aggiunta colonne
        self.client.post(reverse('add-column-post'), columnJustAdd1)
        self.client.post(reverse('add-column-post'), columnJustAdd2)
        self.client.post(reverse('add-column-post'), columnJustAdd3)

        idColumn = Column.objects.get(name='colonnAggiunta1').pk


        datiCardJustAdd1 = {'title': 'Card#1',
                            'description': 'descrizione#1',
                            'storyPoints': '2',
                            'dateExpired': '2018-02-15',
                            'next': 'scrumboard',
                            'boardId': idBoard,
                            'columnId': idColumn}

        datiCardJustAdd2 = {'title': 'Card#2',
                            'description': 'descrizione#2',
                            'storyPoints': '2',
                            'dateExpired': '2018-02-15',
                            'next': 'scrumboard',
                            'boardId': idBoard,
                            'columnId': idColumn}

        #aggiunta card
        self.client.post(reverse('add-card-post'), datiCardJustAdd1)
        self.client.post(reverse('add-card-post'), datiCardJustAdd2)
        #logout
        self.client.get(reverse('sign-out'))

    #test di verifica di accesso non riuscito alla card senza essere inseriti nella stessa board
    def testAccessToCardWithoutBoard(self):
        datiAccessoUser1 = {'username': 'user1',
                            'password': '1234',
                            'next': 'dashboard'}

        datiAccessoUser2 = {'username': 'user2',
                            'password': '1234',
                            'next': 'dashboard'}

        idBoard = Board.objects.get(name='board').pk
        idColumn = Column.objects.get(name='colonnAggiunta1').pk
        idCard1 = Card.objects.get(title='Card#1').pk
        # login utente2 richiesta accesso alla card negato
        self.client.post(reverse('sign-in'), datiAccessoUser2, follow=True)
        response = self.client.get(reverse('card', args=[idBoard, idColumn, idCard1]))
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 404)
        # logout utente2 login utente1 e richiesta accesso card con successo
        self.client.get(reverse('sign-out'))
        self.client.post(reverse('sign-in'), datiAccessoUser1, follow=True)
        response = self.client.get(reverse('card', args=[idBoard, idColumn, idCard1]))
        self.assertNotEqual(response.status_code, 404)
        self.assertEqual(response.status_code, 200)

    #test di verifica di effettiva aggiunta di un utente alla card e successiva rimozione
    def testAddUserToCard(self):
        datiAccessoUser1 = {'username': 'user1',
                            'password': '1234',
                            'next': 'dashboard'}

        idBoard = Board.objects.get(name='board').pk
        idColumn = Column.objects.get(name='colonnAggiunta1').pk
        idCard1 = Card.objects.get(title='Card#1').pk
        idUser1 = User.objects.get(username='user1').pk
        idUser2 = User.objects.get(username='user2').pk

        # login utente1
        self.client.post(reverse('sign-in'), datiAccessoUser1, follow=True)

        datiUserToAddToBoard = {'boardId': idBoard,
                         'userId': idUser2}
        #richiesta aggiunta utente 2 alla board
        self.client.post(reverse('add-user-to-board-post'), datiUserToAddToBoard)
        self.client.get(reverse('card', args=[idBoard, idColumn, idCard1]))

        datiUserToAddToCard = {'boardId': idBoard,
                               'columnId': idColumn,
                               'cardId': idCard1,
                               'userId': idUser2}
        #aggiunta utente2 alla card e controllo presenza utente2 nella lista degli utente della card
        response = self.client.post(reverse('post-card'), datiUserToAddToCard)
        self.assertEquals(response.url, reverse('card', args=[idBoard, idColumn, idCard1]))
        card = Card.objects.get(pk= idCard1)
        self.assertTrue(card.users.filter(pk=idUser2).exists())
        #cancellazione utente2 dalla card e controllo eliminazione
        response = self.client.post(reverse('post-card'), datiUserToAddToCard)
        self.assertEquals(response.url, reverse('card', args=[idBoard, idColumn, idCard1]))
        self.assertFalse(card.users.filter(pk=idUser2).exists())

'''
    TEST DI ACCETTAZIONE MODIFICA COLUMN:
    - testModifyColumn -> test di verifica per la modifica corretta di una colonna esistente
    - testModifyColumn_errore -> test di verifica di segnalazione errore in caso di inserimento nome gia esistente
'''
class ModifyColumnnTest (TestCase):
    '''
        Registrazione e autenticazione di due utenti, creazione di una board
        con all'interno due colonne per poter effettuare il test
    '''

    def setUp(self):
        self.client = Client()
        datiRegistrazione = {'username': 'userJustReg',
                             'email': 'userJustReg@email.com',
                             'password': '1234',
                             'confirm': '1234'}
        # registrazione utente
        self.client.post(reverse('sign-up'), datiRegistrazione)

        datiAccesso = {'username': 'userJustReg',
                       'password': '1234',
                       'next': 'dashboard'}
        #login utente
        self.client.post(reverse('sign-in'), datiAccesso, follow=True)

        boardJustAdd = {'boardname': 'board'}
        #aggiunta board
        self.client.post(reverse('add-board'), boardJustAdd)

        idBoard = Board.objects.get(name='board').pk
        #aggiunta colonna
        columnJustAdd1 = {'columnname': 'colonnAggiunta1', 'boardId': idBoard}
        columnJustAdd2 = {'columnname': 'colonnAggiunta2', 'boardId': idBoard}

        self.client.post(reverse('add-column-post'), columnJustAdd1)
        self.client.post(reverse('add-column-post'), columnJustAdd2)

    #test di verifica di effettiva modifica della colonna
    def testModifyColumn(self):

        idBoard = Board.objects.get(name='board').pk
        idColumn = Column.objects.get(name='colonnAggiunta1').pk

        columnMod = {'newName': 'colonnaModificata', 'boardId': idBoard, 'columnId': idColumn}
        #richiesta modifica colonna con i nuovi dati e controllo avvenuto successo ed effettuata modifica
        self.client.post(reverse('post-column'), columnMod)
        response = self.client.get(reverse('column', args=[idBoard, Column.objects.get(name='colonnaModificata').pk]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Column.objects.filter(name='colonnAggiunta1').exists())

    #test di verifica di segnalazione errore se il nome della colonna inserito esiste gia nella board di riferimento
    def testModifyColumn_errore(self):
        idBoard = Board.objects.get(name='board').pk
        idColumn = Column.objects.get(name='colonnAggiunta1').pk

        columnMod = {'newName': 'colonnAggiunta2', 'boardId': idBoard, 'columnId': idColumn}
        #richiesta di modfica colonna con i nuovi dati e controllo segnalazione di errore
        response = self.client.post(reverse('post-column'), columnMod)
        self.assertContains(response, '*questo nome e gia utilizzato')
        self.assertEqual(Column.objects.get(name='colonnAggiunta1').pk, idColumn)

'''
    TEST DI ACCETTAZIONE MODIFICA CARD:
    - testModifyCard -> test di verifica per la modifica corretta di una card esistente
    - testModifyCard_erroreColumn -> test di verifica di segnalazione errore in caso di inserimento di una colonna che non esiste
    - testModifyCard_erroreTitle -> test di verifica segnalazione di un errore in caso di inserimento titolo card esistente
    - testModifyCard_erroreStoryPoints -> test di verifica di segnalazione errore in caso di inserimento story points <=0
'''
class ModifyCardTest (TestCase):
    '''
        Registrazione e autenticazione di due utenti, creazione di una board
        con all'interno due colonne per poter effettuare il test
    '''

    def setUp(self):
        self.client = Client()
        datiRegistrazione = {'username': 'userJustReg',
                             'email': 'userJustReg@email.com',
                             'password': '1234',
                             'confirm': '1234'}
        #registrazione utente
        self.client.post(reverse('sign-up'), datiRegistrazione)

        datiAccesso = {'username': 'userJustReg',
                       'password': '1234',
                       'next': 'dashboard'}
        #login utente
        response = self.client.post(reverse('sign-in'), datiAccesso, follow=True)
        self.user = response.context['user']

        boardJustAdd = {'boardname': 'board'}
        #aggiunta board
        self.client.post(reverse('add-board'), boardJustAdd)

        idBoard = Board.objects.get(name='board').pk
        columnJustAdd1 = {'columnname': 'colonnAggiunta1', 'boardId': idBoard}
        columnJustAdd2 = {'columnname': 'colonnAggiunta2', 'boardId': idBoard}
        #aggiunta colonne
        self.client.post(reverse('add-column-post'), columnJustAdd1)
        self.client.post(reverse('add-column-post'), columnJustAdd2)

        idColumn = Column.objects.get(name='colonnAggiunta1', board= idBoard).pk

        datiCardJustAdd1 = {'title': 'Card#1',
                            'description': 'descrizione#1',
                            'storyPoints': '2',
                            'dateExpired': '2018-02-15',
                            'next': 'scrumboard',
                            'boardId': idBoard,
                            'columnId': idColumn}

        datiCardJustAdd2 = {'title': 'Card#2',
                            'description': 'descrizione#2',
                            'storyPoints': '2',
                            'dateExpired': '2018-02-15',
                            'next': 'scrumboard',
                            'boardId': idBoard,
                            'columnId': idColumn}
        #aggiunta card
        self.client.post(reverse('add-card-post'), datiCardJustAdd1)
        self.client.post(reverse('add-card-post'), datiCardJustAdd2)

    #test di verifica effettiva modifica di una card esistente
    def testModifyCard(self):
        idBoard = Board.objects.get(name='board').pk
        idColumn = Column.objects.get(name='colonnAggiunta1', board=idBoard).pk
        idCard = Card.objects.get(title='Card#2', column=idColumn).pk

        datiCardMod = { 'newColumn':'colonnAggiunta2',
                        'newTitle': 'CardMod',
                        'newdescription': 'descrizione#mod',
                        'newStoryPoints': '2',
                        'newDateExpired': '2018-02-15',
                        'boardId': idBoard,
                        'columnId': idColumn,
                        'cardId': idCard}
        #richiesta modifica card con nuovi dati e controllo effettiva creazione
        self.client.post(reverse('post-card'), datiCardMod)
        response = self.client.get(reverse('card', args=[idBoard,
                                                         Card.objects.get(title='CardMod').column.pk,
                                                         Card.objects.get(title='CardMod').pk]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Card.objects.filter(title='Card#2').exists())

    #test di verifica segnalazione errore board non esistente
    def testModifyCard_erroreColumn(self):
        idBoard = Board.objects.get(name='board').pk
        idColumn = Column.objects.get(name='colonnAggiunta1', board=idBoard).pk
        idCard = Card.objects.get(title='Card#2', column=idColumn).pk

        datiCardMod = { 'newColumn':'colonnaNonEsistente',
                        'newTitle': 'CardMod',
                        'newdescription': 'descrizione#mod',
                        'newStoryPoints': '2',
                        'newDateExpired': '2018-02-15',
                        'boardId': idBoard,
                        'columnId': idColumn,
                        'cardId': idCard}
        #richiesta modifica card con nuovi dati e controllo segnalazione errore
        response = self.client.post(reverse('post-card'), datiCardMod)
        self.assertContains(response, '*questa colonna non esiste')

    #test di verifica segnalazione errore title gia utilizzato da una card della stessa board
    def testModifyCard_erroreTitle(self):
        idBoard = Board.objects.get(name='board').pk
        idColumn = Column.objects.get(name='colonnAggiunta1', board=idBoard).pk
        idCard = Card.objects.get(title='Card#2', column=idColumn).pk

        datiCardMod = { 'newColumn':'colonnAggiunta1',
                        'newTitle': 'Card#1',
                        'newdescription': 'descrizione#mod',
                        'newStoryPoints': '2',
                        'newDateExpired': '2018-02-15',
                        'boardId': idBoard,
                        'columnId': idColumn,
                        'cardId': idCard}
        # richiesta modifica card con nuovi dati e controllo segnalazione errore
        response = self.client.post(reverse('post-card'), datiCardMod)
        self.assertContains(response, '*questo nome e gia utilizzato nella colonna di destinazione')

    #test di verifica segnalazione errore story points <=0
    def testModifyCard_erroreStoryPoints(self):
        idBoard = Board.objects.get(name='board').pk
        idColumn = Column.objects.get(name='colonnAggiunta1', board=idBoard).pk
        idCard = Card.objects.get(title='Card#2', column=idColumn).pk

        datiCardMod = { 'newColumn':'colonnAggiunta1',
                        'newTitle': 'CardMod',
                        'newdescription': 'descrizione#mod',
                        'newStoryPoints': '-1',
                        'newDateExpired': '2018-02-15',
                        'boardId': idBoard,
                        'columnId': idColumn,
                        'cardId': idCard}
        # richiesta modifica card con nuovi dati e controllo segnalazione errore
        response = self.client.post(reverse('post-card'), datiCardMod)
        self.assertContains(response, '*inserire un numero maggiore di  0')

        datiCardMod = {'newColumn': 'colonnAggiunta1',
                       'newTitle': 'CardMod',
                       'newdescription': 'descrizione#mod',
                       'newStoryPoints': '0',
                       'newDateExpired': '2018-02-15',
                       'boardId': idBoard,
                       'columnId': idColumn,
                       'cardId': idCard}
        # richiesta modifica card con nuovi dati e controllo segnalazione errore
        response = self.client.post(reverse('post-card'), datiCardMod)
        self.assertContains(response, '*inserire un numero maggiore di  0')

'''
    TEST DI ACCETTAZIONE BURNDOWN:
    - testBurndown -> controllo se i valori delle statistiche siano presenti all'interno della pagina burndown e controllo correttezza
'''
class BurndownTest (TestCase):
    '''
        Registrazione e autenticazione di due utenti, creazione di una board
        con all'interno tre colonne, inserimento di 5 card, in modo da
        poter effettuare il test
    '''

    def setUp(self):
        self.client = Client()
        datiUser1 = {'username': 'user1',
                     'email': 'user1@email.com',
                     'password': '1234',
                     'confirm': '1234'}

        #registrazione utente
        self.client.post(reverse('sign-up'), datiUser1)

        datiAccessoUser1 = {'username': 'user1',
                            'password': '1234',
                            'next': 'dashboard'}

        #login utente
        self.client.post(reverse('sign-in'), datiAccessoUser1, follow=True)

        boardJustAdd = {'boardname': 'board'}
        #aggiunta board
        self.client.post(reverse('add-board'), boardJustAdd)

        idBoard = Board.objects.get(name='board').pk
        columnJustAdd1 = {'columnname': 'colonnAggiunta1', 'boardId': idBoard}
        columnJustAdd2 = {'columnname': 'colonnAggiunta2', 'boardId': idBoard}
        columnJustAdd3 = {'columnname': 'colonnAggiunta3', 'boardId': idBoard}
        #aggiunta colonne
        self.client.post(reverse('add-column-post'), columnJustAdd1)
        self.client.post(reverse('add-column-post'), columnJustAdd2)
        self.client.post(reverse('add-column-post'), columnJustAdd3)

        idColumn1 = Column.objects.get(name='colonnAggiunta1').pk
        idColumn2 = Column.objects.get(name='colonnAggiunta2').pk
        idColumn3 = Column.objects.get(name='colonnAggiunta3').pk

        datiCardJustAdd1 = {'title': 'Card#1',
                            'description': 'descrizione#1',
                            'storyPoints': '5',
                            'dateExpired': '2018-02-15',
                            'next': 'scrumboard',
                            'boardId': idBoard,
                            'columnId': idColumn1}

        datiCardJustAdd2 = {'title': 'Card#3',
                            'description': 'descrizione#3',
                            'storyPoints': '5',
                            'dateExpired': '2018-09-15',
                            'next': 'scrumboard',
                            'boardId': idBoard,
                            'columnId': idColumn1}

        datiCardJustAdd3 = {'title': 'Card#3',
                            'description': 'descrizione#1',
                            'storyPoints': '5',
                            'dateExpired': '2018-08-15',
                            'next': 'scrumboard',
                            'boardId': idBoard,
                            'columnId': idColumn2}

        datiCardJustAdd4 = {'title': 'Card#4',
                            'description': 'descrizione#4',
                            'storyPoints': '5',
                            'dateExpired': '2018-02-15',
                            'next': 'scrumboard',
                            'boardId': idBoard,
                            'columnId': idColumn2}

        datiCardJustAdd5 = {'title': 'Card#5',
                            'description': 'descrizione#5',
                            'storyPoints': '5',
                            'dateExpired': '2018-02-15',
                            'next': 'scrumboard',
                            'boardId': idBoard,
                            'columnId': idColumn3}
        #aggiunta card
        self.client.post(reverse('add-card-post'), datiCardJustAdd1)
        self.client.post(reverse('add-card-post'), datiCardJustAdd2)
        self.client.post(reverse('add-card-post'), datiCardJustAdd3)
        self.client.post(reverse('add-card-post'), datiCardJustAdd4)
        self.client.post(reverse('add-card-post'), datiCardJustAdd5)

    #test per la verifica della correttezza delle operazioni in burndowm
    def testBurndown(self):
        idBoard = Board.objects.get(name='board').pk
        #richiamo funzioni di calcolo statistiche
        column = Column.objects.filter(board=idBoard)
        cardNum = Card.objects.filter(column__pk__in=column).count()  # numero di card
        cardExpire = Card.objects.filter(column__pk__in=column,
                                         dateExpire__lt=datetime.datetime.now()).count()  # numero di card scadute
        numStoryPoints = Card.objects.filter(column__pk__in=column).aggregate(Sum('storyPoints'))[
            'storyPoints__sum']  # numero storypoints utilizzati
        numCardColumn = Card.objects.filter(column__pk__in=column).values('column').annotate(
            Count('title'))  # numero carte per colonna
        # asseblaggio numero card colonna con rispettivo nome
        numCardColumn = [{'columnname': Column.objects.get(pk=elem['column']).name, 'num': elem['title__count']} for
                         elem in numCardColumn]
        # unione con le colonne che hanno zero card
        numCardColumn.extend(
            [{'columnname': elem.name, 'num': 0} for elem in column if not Card.objects.filter(column=elem).exists()])
        #controllo sul raggiungimento della pagina burndown e controllo presenza e correttezza dati
        response = self.client.get(reverse('burndown', args= [idBoard]))
        self.assertEqual(response.status_code, 200)

        self.assertEqual(cardNum,5)
        self.assertEqual(cardExpire, 3)
        self.assertEqual(numStoryPoints, 25)
        self.assertContains(response, cardNum)
        self.assertContains(response, cardExpire)
        self.assertContains(response, numStoryPoints)

        for column in numCardColumn:
            self.assertContains(response, column['num'])
