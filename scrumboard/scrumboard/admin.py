from django.contrib import admin
from models import *
#  /*------------------------------------------------------------------------*/
#   * Progetto - Ingegneria del Software - admin.py
#  /*------------------------------------------------------------------------*/
#   * Nome:         - Scrumboard
#   * Descrizione:  - Applicazione Web per la gestione di una board scrum
#   * Autori:       - Pilloni Raffaele  - 65151
#                   - Meloni Giacomo    - 65181
#                   - Ziantoni Stefano  - 65197
#                   - Ibba Andrea       - 65258
#  /*------------------------------------------------------------------------*/

#registazione modello nell'admin di django
admin.site.register(Board)
admin.site.register(Column)
admin.site.register(Card)