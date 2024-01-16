from django.shortcuts import render, get_object_or_404
from .models import Produk, Kategori, Kontak, Profil, Slide, Statis, ChatID
from toyibcart.models import Transaksi, DetailTransaksi
from django.db.models import Count
from django.views.generic import View
from django.contrib import messages

import json
import urllib.request
import datetime
from django.conf import settings
from django.core.paginator import Paginator
from toyibcart.forms import CartAddProductForm
from toyibcart.keranjang import Cart
from .telegram_utill import send_telegram_message
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import Q



def beranda(request):
    kategori = Kategori.objects.filter(aktif=True).order_by('-id')
    slider = Slide.objects.filter(aktif=True).order_by('-id')
    jumlahkategori = Kategori.objects.all().annotate(produk_count=Count('produks')).order_by('-id')
    trending = Produk.objects.order_by('-dibeli')
    cart_product_form = CartAddProductForm()
    context = {
        "judul": "Halaman Beranda",
        "kategori" : kategori,
        "judul": "Halaman Beranda",
        "jumlahkategori":jumlahkategori,
        "slide": slider,
        "trending":trending,
        "cart_product_form": cart_product_form, 
        }
    return render(request, 'beranda.html', context)

def profil(request):
    profil = Profil.objects.all().order_by('-id')[:1]
    context = {
        "judul": "Halaman Profil",
        "profil":profil,
        }
    return render(request, 'profil.html', context)


class KontakView(View):
    def get(self, request):
        context = {
            'judul': 'Halaman Kontak',
            }
        return render(request, 'kontak.html', context)
    
    def post(self, request):
        context = {
            'judul': 'Halaman Kontak',
            'data': request.POST,
            'has_error': False
            }
            
        nama = request.POST.get('nama')
        no_whatsup = request.POST.get('whatsapp')
        subject = request.POST.get('subject')
        email = request.POST.get('email')
        pesan = request.POST.get('pesan')

        if nama == "":
            messages.error(request, 'Nama masih kosong')
            context['has_error'] = True

        if no_whatsup == "":
            messages.error(request, 'No whatsapp masih kosong')
            context['has_error'] = True

        if subject == "":
            messages.error(request, 'Subject masih kosong')
            context['has_error'] = True
        
        if pesan == "":
            messages.error(request, 'Pesan masih kosong')
            context['has_error'] = True
        
        recaptcha_response = request.POST.get('g-recaptcha-response')
        url = 'https://www.google.com/recaptcha/api/siteverify'
        values = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
            }
        data = urllib.parse.urlencode(values).encode()
        req = urllib.request.Request(url, data=data)
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode())

        # print(result['success'])
        if result['success']== False:
            messages.error(request, 'CaptCha Masih Belum dicentang')
            context['has_error'] = True
                        
        if context['has_error']:
            return render(request, 'kontak.html', context, status=400)
        
        kontak = Kontak.objects.create(nama=nama, email=email, no_whatsup=no_whatsup, subject=subject, isi=pesan)
        kontak.save()
        context = {
             'judul': 'Halaman Kontak',
             'data': "",
             'has_error': False
        }
        messages.success(request, 'Pesan sudah terkirim, silakan tunggu respon selanjutnya!')
        return render(request, 'kontak.html', context, status=400)

class CheckoutView(View):
    def get(self, request):
        context = {
            'judul': 'Halaman Checkout',
            }
        return render(request, 'checkout.html', context)
    
    def post(self, request):
        context = {
            'judul': 'Halaman checkout',
            'data': request.POST,
            'has_error': False
            }
        
        grantotal = request.POST.get('grantotal')
        nama_depan = request.POST.get('nama_depan')
        nama_belakang = request.POST.get('nama_belakang')
        alamat = request.POST.get('alamat')
        provinsi = request.POST.get('provinsi')
        kabupaten = request.POST.get('kabupaten')
        kecamatan = request.POST.get('kecamatan')
        kode_post = request.POST.get('kode_post')
        email = request.POST.get('email')
        whatsapp = request.POST.get('whatsapp')
        no_transaksi = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        
        if grantotal == "0":
             messages.error(request, 'Anda belum berbelanja, Silakan belanja terlebih dahulu')
             context['has_error'] = True
        if nama_depan == "":
            messages.error(request, 'Nama Depan Masih kosong')
            context['has_error'] = True
        if alamat == "":
            messages.error(request, 'Alamat Masih kosong')
            context['has_error'] = True
        if provinsi == "":
            messages.error(request, 'Provinsi Masih kosong')
            context['has_error'] = True
        if kabupaten == "":
            messages.error(request, 'Kabupaten Masih kosong')
            context['has_error'] = True
        if kecamatan == "":
            messages.error(request, 'Kecamatan Masih kosong')
            context['has_error'] = True
        if kode_post == "":
            messages.error(request, 'Kode Post Masih kosong')
            context['has_error'] = True
        if whatsapp == "":
            messages.error(request, 'Whatsapp Masih kosong')
            context['has_error'] = True
        if context['has_error']:
            return render(request, 'checkout.html', context, status=400)
        
        transaksi = Transaksi.objects.create(no_transaksi=no_transaksi,
                                              nama_depan=nama_depan,
                                              nama_belakang=nama_belakang,
                                              alamat=alamat,
                                              provinsi=provinsi,
                                              kabupaten=kabupaten,
                                              kecamatan=kecamatan,
                                              kode_post=kode_post,
                                              email=email,
                                              whatsapp=whatsapp,
                                              total_transaksi=grantotal )
        transaksi.save()
        keranjang = Cart(request)
        for r in keranjang:

            instance_detail= DetailTransaksi(
                no_transaksi = no_transaksi,
                produk = r['product'],
                jumlah = r['quantity'],
            )
            instance_detail.save()

            dibeliupdate=Produk.objects.get(nama_produk=r['product'])
            dibeliupdate.dibeli+=int(r['quantity'])
            dibeliupdate.save()

        chats = ChatID.objects.filter(aktif=True)
        for chat in chats:
            grantotal_formatted = f"Rp. {intcomma(grantotal)}"
            message = f"Assalamualaikum Wr Wb,\n\nNo Transaksi: <b>{no_transaksi}</b>\nNama: <b>{nama_depan} {nama_belakang}</b>\nNo whatsapp: <b>{whatsapp}</b>\nAlamat: <b>{alamat}</b>\nTotal Transaksi: <b>{grantotal_formatted}</b>\n\nTerimakasih, Salam Clarak Store dan Wssalamualaikum Wr Wb."
            send_telegram_message(chat.chatid, message)
            
        keranjang.clear()
        context = {
            'judul': 'Halaman checkout',
            'data': "",
            'has_error': False
        }
        messages.success(request, 'Pesanan Anda akan segera diproses, silakan tunggu akan ada respon selanjutnya!')
        return render(request, 'checkout.html', context, status=400)


def produk(request, kategori_slug, slug):
    produk = get_object_or_404(Produk, slug=slug)
    related = Produk.objects.filter(kategori=produk.kategori.id)
    jml = related.count()
    cart_product_form = CartAddProductForm()

    context = {
        "judul": "Halaman Produk Kami",
        "produk": produk,
        "related": related,
        "jml": jml,
        "cart_product_form": cart_product_form,
    }
    return render(request, 'produk.html', context)

def pemesanan(request):
    context = {
        "judul": "Halaman Pemesanan",
        }
    return render(request, 'pemesanan.html', context)

def kategori(request, slug):
    kategori = get_object_or_404(Kategori, slug=slug)
    produk = kategori.produks.order_by('-id')
    halaman_tampil = Paginator(produk, 2)
    halaman_url = request.GET.get('halaman', 1)
    halaman_produk = halaman_tampil.get_page(halaman_url)
    cart_product_form = CartAddProductForm()
    
    if halaman_produk.has_previous():
        url_previous = f'?halaman={halaman_produk.previous_page_number()}'
    else:
        url_previous = ''
    
    if halaman_produk.has_next():
        url_next = f'?halaman={halaman_produk.next_page_number()}'
    else:
        url_next = ''
    
    context = {
        "judul": "Halaman Kategori",
        "detailkategori": kategori,
        "produk": halaman_produk,
        "previous": url_previous,
        "next": url_next,
        "cart_product_form": cart_product_form,
        }
    return render(request, 'kategori.html', context)

def cari(request):
    datakategori=request.GET.get('kategori')
    datakata=request.GET.get('kata')
    if datakategori == "all":
        hasilcari = Produk.objects.filter(Q(nama_produk__icontains=datakata)).order_by('-id')
    else:
        hasilcari = Produk.objects.filter(Q(nama_produk__icontains=datakata & Q(kategori__id__exact=datakategori))).order_by('-id')
    
    cart_product_form = CartAddProductForm()
    jmlproduk = hasilcari.count()
    context = {
        "judul" : "Halaman Cari",
        "cart_product_form" : cart_product_form,
        "hasilcari" : hasilcari,
        "jmlproduk" : jmlproduk,
    }
    print(hasilcari)
    return render(request, 'cari.html', context)

def kategoriberanda(request):
    kategori = Kategori.objects.filter(aktif=True).order_by('-id')
    return {'kategori':kategori}

def modalberita(request):
    modalproduk = Produk.objects.order_by('-id')
    return {'modalproduk':modalproduk}

def statisweb(request):
    statis = Statis.objects.get(id=1)
    return {'statis':statis}







