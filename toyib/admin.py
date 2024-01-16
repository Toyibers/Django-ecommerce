from django.contrib import admin

class KategoriAdmin(admin.ModelAdmin):
    list_display = ("nama", "aktif","banner_satu","banner_dua",)
    prepopulated_fields = {"slug": ("nama",)} 

class DataProdukAdmin(admin.ModelAdmin):
    list_display = ("nama_produk", "gambar","harga","no_whatsup",)
    prepopulated_fields = {"slug": ("nama_produk",)}

from .models import Kategori, Produk, Slide, Kontak,Profil,Statis, ChatID

admin.site.register(Kategori,KategoriAdmin)
admin.site.register(Produk,DataProdukAdmin)
admin.site.register(Slide)
admin.site.register(Kontak)
admin.site.register(Profil)
admin.site.register(Statis)
admin.site.register(ChatID)