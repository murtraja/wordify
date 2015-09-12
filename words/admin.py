from django.contrib import admin
from words.models import Word, UserProfile,GroupFinalResult,GroupResultTable,ResultTable,FinalResult

# Register your models here.
admin.site.register(Word)
admin.site.register(UserProfile)
admin.site.register(GroupResultTable)
admin.site.register(GroupFinalResult)
admin.site.register(FinalResult)
admin.site.register(ResultTable)