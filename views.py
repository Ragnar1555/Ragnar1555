from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import TweetForm, CommentForm, ReplyForm, ImageForm, PostCategoryForm, ImageCommentForm
from .models import Post, Comment, Images, Reply, PostCategory, Cart,UsersOrders, Brand, Published, Shoutout, Offer, CartHistory, Order, Promotions, JoinedCategory, Category, Color, Model, Size, Visit_logs, ImageComment,PinImage, Refer_Image, Favourites, Notify, Market, JoinRequest, Friend, Friend_Request, friend_suggestion
from users.models import Business, Profile
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.forms import modelformset_factory
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from math import ceil
from django.views.decorators.csrf import csrf_exempt
import datetime
import  json
from users.models import BusinessCategory
from django.core.files.storage import FileSystemStorage

import django
from django.views.generic import View, ListView, DetailView, CreateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers
#import pyperclip
notifs ={}


class CategoryPosts(View):
    def get(self, request, category):
        user = request.user
        users =User.objects.all()
        friends =Friend.objects.filter(user = user)
        friends_reqs=Friend_Request.objects.filter(to = user)
        sent_friends_reqs=Friend_Request.objects.filter(user = user)
        businesses =Business.objects.all()
        notifs =Notify.objects.filter(to_user_id = request.user.id, status = 1)

        business = Business.objects.filter(id= request.POST.get('busiId'))
        print(business)

        user_county=user.profile.county
        user_town = user.profile.town
        categsx = BusinessCategory.objects.filter(county=user_county, town =user_town)
        context ={'friends':friends,  'categsx':categsx, 'users':users, 'businesses':businesses,  'notifs':notifs}
        return render(request, 'blog/posts.html', context = context)
    def post(self, request, category):
        pass


class FriendList(View):
    def get(self, request):
        user = request.user
        users =User.objects.all()
        friends =Friend.objects.filter(user = user)
        friends_reqs=Friend_Request.objects.filter(to = user)
        sent_friends_reqs=Friend_Request.objects.filter(user = user)
        businesses =Business.objects.all()
        notifs =Notify.objects.filter(to_user_id = request.user.id, status = 1)

        user_county=user.profile.county
        user_town = user.profile.town
        categsx = BusinessCategory.objects.filter(county=user_county, town =user_town)
        friends_ids =list()
        for i in friends:
            friends_ids.append(i.friend_id)
        req_ids =list()
        for i in sent_friends_reqs:
            req_ids.append(i.to_id)
        context ={'friends':friends, 'friends_ids':friends_ids, 'req_ids':req_ids, 'friends_reqs':friends_reqs, 'categsx':categsx, 'users':users, 'businesses':businesses,  'notifs':notifs}
        return render(request, 'blog/friend_zone.html', context =context)
    def post(self, request):
        user = request.user
        connect_id = request.POST.get('con_id')
        friends =Friend.objects.filter(user = user)
        friends_reqs=Friend_Request.objects.filter(to = user)
        userx =User.objects.get(id = connect_id)
       
        friends_ids =list()
        for i in friends:
            friends_ids.append(i.friend_id)
        req_ids =list()
        for i in friends_reqs:
            req_ids.append(i.to_id)
        if connect_id:
            if Friend_Request.objects.filter( user = request.user, to_id = connect_id):
                Friend_Request.objects.filter( user = request.user, to_id= connect_id).delete()
            else:
                Friend_Request.objects.create( user = request.user, to_id= connect_id)
        if request.is_ajax(): 
            htmlxc = render_to_string(template_name = 'blog/connectBtn.html', context = {'friends_ids':friends_ids, 'req_ids':req_ids, })
            data_dict = {"htmlviewnmm": htmlxc}
            return JsonResponse(data=data_dict, safe=False)

class PinList(View):
    def get(self, request):
        user = request.user
        markets = Market.objects.all()
        businesses =Business.objects.all()
        notifs =Notify.objects.filter(to_user_id = request.user.id, status = 1)
        friends =Friend.objects.filter(user = request.user)

        #Notify.objects.filter(action ='accepted your request').update(action ='accepted your request to join')
        friends_ids =list()
        user_county=user.profile.county
        user_town = user.profile.town
        categsx = BusinessCategory.objects.filter(county=user_county, town =user_town)
        for i in friends:
            friends_ids.append(i.friend_id)
        pins= PinImage.objects.filter(user = request.user)
        posts =list()
        for f in pins:
            posts.append(f.post)
        context ={'markets':markets, 'friends': friends, 'pins':pins, 'businesses':businesses, 'categsx':categsx, 'posts':posts, 'notifs':notifs}
        return render(request, 'blog/pinned_post.html', context= context)



    def post(self, request):
        post=get_object_or_404(Post, id=request.POST.get('id'))
        user_id=post.user_id
        user=User.objects.get(id=user_id)
        is_pinned=False
        if post.pins.filter(id=request.user.id).exists():
            post.pins.remove(request.user)
            PinImage.objects.filter(image = post.image, user = request.user, post = post).delete()
            is_pinned=False
            action = 'unpinned your post'
            Notify.objects.create(from_user = request.user, to_user =post.user, action = action, what = 'post', what_id = post.id )
        return HttpResponse('')

class PromoList(View):
    def get(self, request):
        user = request.user
        markets = Market.objects.all()
        businesses =Business.objects.all()
        notifs =Notify.objects.filter(to_user_id = request.user.id, status = 1)
        friends =Friend.objects.filter(user = request.user)
        promotions = Promotions.objects.filter(user = request.user)
        posts_promoted = list()
        for v in promotions:
            posts_promoted.append(v.post)
            print(posts_promoted)

        #Notify.objects.filter(action ='accepted your request').update(action ='accepted your request to join')
        friends_ids =list()
        user_county=user.profile.county
        user_town = user.profile.town
        categsx = BusinessCategory.objects.filter(county=user_county, town =user_town)
        for i in friends:
            friends_ids.append(i.friend_id)
        offers = Offer.objects.filter(user = request.user)
        context ={'markets':markets, 'friends': friends,  'posts_promoted':posts_promoted, 'offers':offers, 'businesses':businesses, 'categsx':categsx,  'notifs':notifs}
        return render(request, 'blog/promos.html', context= context)
    def post(self, request):
        if request.POST.get('promoid'):
            post =get_object_or_404(Post, id = request.POST.get('promoid'))
            Promotions.objects.get(post = post, user = request.user).delete()

        if request.POST.get('offertext'):
            name = request.POST.get('offertext')
            Offer.objects.create(user = request.user, name = name)

        return redirect('promotions')


class MarketList(View):
    def get(self, request):
        markets = Market.objects.all()
        businesses =Business.objects.all()
        notifs =Notify.objects.filter(to_user_id = request.user.id, status = 1)
        friends =Friend.objects.filter(user = request.user)
        friends_ids =list()
        for i in friends:
            friends_ids.append(i.friend_id)
        context ={'markets':markets, 'friends': friends, 'businesses':businesses, 'notifs':notifs}
        return render(request, 'blog/markets.html', context= context)
        

class ShoutView(View):
    def get(self, request):
        category = PostCategory.objects.filter(user=request.user)
        businesses=Business.objects.all()
        friends=Friend.objects.all()
        notifs =Notify.objects.filter(to_user_id = request.user.id, status = 1)
        draft = Shoutout.objects.filter(user = request.user, status = 'draft')
        for d in draft:
            print(d.text)
        context={'category': category, 'friends': friends, 'businesses': businesses, 'notifs':notifs, 'draft': draft}
        return render(request, 'blog/shout.html', context= context)
    def post(self, request):


        if request.POST.get('btnclose'):
            Shoutout.objects.filter(user = request.user, status = 'draft').delete()
        elif request.POST.get('pubtn'):
            Shoutout.objects.filter(user = request.user, status = 'draft').update(status = 'published')
        if Shoutout.objects.filter(user = request.user, status = 'draft'):
            print('Unex')
        else:
            try:
                cate = request.POST.get('Prodcategory')
                text = request.POST.get('ShoutText')
                myfile = request.FILES.get('imagefieldxb')
                fs = FileSystemStorage()
                filename = fs.save(myfile.name, myfile)
                xl=Shoutout(image= filename, user = request.user, text = text, status = 'draft')
                xl.save()
                
            except AttributeError as e:
               pass
            

        return redirect('shout')

class HomeView(View):
    def get(self, request):
        users=User.objects.all()
        businesses=Business.objects.all()
        posts=Post.objects.filter(user = request.user)
        #Business.objects.all().delete()
        draft = Shoutout.objects.filter(status = 'published')
        posts_likes =0
        for p in posts:
            posts_likes += p.likes.count()
        query=request.GET.get('q')
        user=request.user
        if query:
            businesses=Business.objects.filter(Category__icontains=query)
        category ={}
        #Profile.objects.filter(user =user).update(county ='Nairobi', town ='Mathare')
        category = Category.objects.filter(user=request.user)
        user_county=user.profile.county
        user_town = user.profile.town
        categsx = BusinessCategory.objects.filter(county=user_county, town =user_town)
        friends =Friend.objects.filter(user = request.user)

        myreqs= Friend_Request.objects.filter(user =user)
        to_ids = list()
        for i in myreqs:
            to_ids.append(i.to_id)
        markets =Market.objects.all()
        is_sent_join=False
        business_favos ={}
        for d in markets:
            is_sent_join =False
            if d.requesters.filter(id=request.user.id).exists():
                is_sent_join =True
            else:
                is_sent_join =False
        is_favourite=False
        for business in businesses: 
            rating = business.business_favos.count() + business.views
            Business.objects.filter(id = business.id).update(rating = rating)
            business_favos = business.business_favos.all()[:5]
            if Favourites.objects.filter(user_id = user.id, bus_id = business.id):
                is_favourite =True
        favourites ={}
        favos=Favourites.objects.filter(user=request.user)
        logs =Visit_logs.objects.filter(user_id =user.id)
        new_posts ={}
        is_friend =False
        for log in logs:
            new_posts = log.no_of_posts - log.no_of_posts_lv
            for business in businesses:
                Visit_logs.objects.filter(business_id = business.id, user_id =user.id).update(diff = new_posts )
        notifs =Notify.objects.filter(to_user_id = request.user.id, status = 1)
        users_in_friend_request =list()
        #XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        paginator =Paginator(businesses, 2)
        page_numer =request.GET.get('page')
        businesses_obj = paginator.get_page(page_numer)
        images =Images.objects.all()
        ofs = list()
        offers = Offer.objects.all()


        promotions = Promotions.objects.all()

        return render(request, 'blog/home_business.html', context={ 'businesses':businesses, 'promotions':promotions, 'offers':offers, 'draft':draft, 'is_sent_join':is_sent_join,
            'business_favos':business_favos,  'new_posts':new_posts, 'logs': logs,  'images':images,  
            'friends':friends, 'to_ids':to_ids, 'posts_likes':posts_likes,'users':users, 'categsx': categsx, 'favourites':favourites, 'favos':favos, 'category':category,  'markets':markets, 'posts':posts, 
             'is_favourite':is_favourite, 'user':user,  'notifs':notifs}
    )

    def post(self, request):
        cat =request.POST.get('busCat') 
        businesses= {}
        bus_favs ={}
        if cat == 'Nearest':
            businesses= Business.objects.all()
        elif cat == 'Favourites':
            businessesy= Business.objects.all()
            bus_favs = request.user.user_favs.all()
            businesses =list()
            for f in businessesy:
                for g in bus_favs:
                    if f.id == g.bus_id :
                        businesses.append(f)
        elif cat == 'High-Rated':
            businessesx= Business.objects.all()
            businesses  =list()
            for g in businessesx:
                if g.rating >50000:
                    businesses.append(g)
        elif cat == 'Recent':
            businesses= Business.objects.all()[:5]
        if request.is_ajax():
            html = render_to_string(template_name = 'blog/business.html', context = {'businesses':businesses, 'bus_favs': bus_favs})
            htmlxc = render_to_string(template_name = 'blog/connectBtn.html', context = {'bs':business})
            data_dict = {"htmlviewn": html, "htmlviewnmm": htmlxc}
            return JsonResponse(data=data_dict, safe=False)
        
def load_more(request):
    offset =int(request.POST['offset'])
    limit = 2
    businesses =Business.objects.all()[offset:offset + limit]
    totalData = Business.objects.count()
    businesses_json = serializers.serialize('json', businesses)
    return JsonResponse(data = {'businesses': businesses_json, 'totalData':totalData})
def discover_nearest(request):
    user =request.user
    users = User.objects.all()
    user_county=user.profile.county
    user_town = user.profile.town
    markets =Market.objects.all()
    businesses_near=Business.objects.filter(county=user_county, town =user_town).order_by('-joined')
    categsx = BusinessCategory.objects.filter(county=user_county, town =user_town)

    for g in categsx:
        bss = Business.objects.filter(Category= g.name, county=user_county, town =user_town)
        print(bss.count())

    return render(request, 'blog/discover_nearest.html', context={'businesses': businesses_near,  'markets':markets, 'users':users, 'category': categsx})
def publish_images(request, pk):
    ima=Images.objects.get(pk=pk)
    post_id=ima.post_id
    query=request.POST.get('Q')

    if query:
        Images.objects.filter(id=pk).update(caption = query)
        return redirect('blog-post_comment')
class AddProductMarket(DetailView):
    def get(self, request, pk):
        market = get_object_or_404(Market, id =pk)
        categs = Category.objects.filter(user_id = request.user.id)
        businesses=Business.objects.all()
        user = request.user
        markets =Market.objects.all()
        friends =Friend.objects.filter(user =user)
        user_county=user.profile.county
        user_town = user.profile.town
        notifs =Notify.objects.filter(to_user_id = request.user.id, status = 1)
        categsx = BusinessCategory.objects.filter(county=user_county, town =user_town)
        context={'markets':markets, 'categs':categs, 'friends':friends, 'businesses':businesses, 'categsx':categsx,  'notifs':notifs}
        return render(request, 'blog/market_posting.html',  context)


    def post(self, request, pk):
        market = get_object_or_404(Market, id =pk)
        user =request.user
        files=request.FILES.getlist('addtionalProd_images')
        file = request.FILES.get('prod_image')
        video =request.FILES.get('prod_vid')
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)


        catv = Category.objects.get( name = request.POST.get('category'), user_id = request.user.id,)
        cat =PostCategory.objects.get(name = request.POST.get('sbcategory'), cat =catv)
        if catv and cat:
            cat_instance  = Post.objects.create(
                                user = request.user,
                                price =request.POST.get('priceInput'), 
                                subcat =cat, 
                                description =request.POST.get('ProductDescription'), 
                                video =video, 
                                image =filename,  
                                where =market.name,
                                color = request.POST.get('colorInput'), 
                                model = request.POST.get('modelInput'),
                                size  = request.POST.get('sizeInput'))
            Visit_logs.objects.filter(business_id = user.business.id).update(no_of_posts = user.user_posts_drafts.count())
            if request.POST.get('colorInput'):
                try:
                    color = Color.objects.get(col = request.POST.get('colorInput'))
                except Exception as e:
                    Color.objects.create(subcat = cat, number = 1, col = request.POST.get('colorInput'))
                else:
                    color = Color.objects.get(col = request.POST.get('colorInput'))
                    number =color.number + 1
                    Color.objects.filter(col = request.POST.get('colorInput')).update(number = number)

            if request.POST.get('modelInput'):
                try:
                    model = Model.objects.get(mod = request.POST.get('modelInput'))
                except Exception as e:
                    Model.objects.create(subcat =cat, number = 1, mod = request.POST.get('modelInput'))
                else:
                    model = Model.objects.get(mod = request.POST.get('modelInput'))
                    number = model.number + 1
                    Model.objects.filter(mod = request.POST.get('modelInput')).update(number =number)
                
            if request.POST.get('sizeInput'):
                try:
                    size = Size.objects.get(size = request.POST.get('sizeInput'))
                except Exception as e:
                    Size.objects.create(subcat =cat, number =1, size =request.POST.get('sizeInput'))
                else:
                    size = Size.objects.get(size = request.POST.get('sizeInput'))
                    number =size.number + 1
                    Size.objects.filter(size = request.POST.get('sizeInput')).update(number =number)

                    
            action = 'added new post'
            #Notify.objects.create(from_user = request.user, to_user =0, action = action, what = 'business', what_id = user.business.id )
        for f in files:
            photo =Images.objects.create(post=cat_instance, user = request.user, image=f)

        return redirect('blog-AddProdMarket', pk =pk)
class NarketView(DetailView):
    def get(self, request, pk):
        market = get_object_or_404(Market, id =pk)
        markets = Market.objects.all()
        Joinedcats=JoinedCategory.objects.filter(market = market)
        user =request.user
        user_county=user.profile.county
        user_town = user.profile.town
        markets =Market.objects.all()
        businesses =Business.objects.all()
        friends =Friend.objects.filter(user = user)
        businesses_near=Business.objects.filter(county=user_county, town =user_town).order_by('-joined')[:10]
        market_notifications = Notify.objects.filter(to_user =request.user)
        categs = PostCategory.objects.filter(user_id = request.user.id)
        requests_to_join = JoinRequest.objects.filter(market_id = market.id)
        favos=Favourites.objects.filter(user = request.user)
        posts_user =Post.objects.filter(user = request.user)
        posts = Post.objects.filter(where = market.name)
        categsx =BusinessCategory.objects.all()
        notifs =Notify.objects.filter(to_user_id = request.user.id, status = 1)

        busreqs = list()
        for i in market.requesters.all():
            busreqs.append(i.business)

        busjoinerrs = list()
        for f in market.joiners.all():
            busjoinerrs.append(f.business)
        
        joinedcats = list()
        for f in Joinedcats:
            joinedcats.append(str())
        return render(request, 'blog/market_home.html', context = {"market":market, 'busjoinerrs':busjoinerrs, 'busreqs':busreqs, 'Joinedcats':Joinedcats, 'categsx':categsx, 'bs':request.user.business, 'friends':friends, 'businesses':businesses, 'zoners':businesses_near, 'favos':favos, 'categs':categs, 'notifs':requests_to_join, 'posts':posts})
    def post(self, request, pk):
        market = get_object_or_404(Market, id =pk)
        if request.FILES.get('imagefiles'):
            files = request.FILES.getlist('imagefiles')
            cat_instance  = Post.objects.create( user = request.user, category = request.POST.get('category'), status = 'draft', where =market.name)
            for f in files:
                fs = FileSystemStorage()
                filename = fs.save(f.name, f)
                photo =Images.objects.create(post=cat_instance, image=f, user =request.user)
            return redirect('blog-post_comment')

        if request.POST.get('id'):
            userrequested = get_object_or_404(User, id =request.POST.get('id'))
    

            if not market.joiners.filter(id = request.user.id).exists() and market.user.id == request.user.id: 
                JoinedCategory.objects.create(business = request.user.business, market = market, category = userrequested.business.Cate.name, number=1)
                market.joiners.add(request.user)

            if market.joiners.filter(id = userrequested.id).exists():
                market.joiners.remove(userrequested)
                market.requesters.remove(userrequested)
            else:

                if  JoinedCategory.objects.filter(category = request.POST.get('cat'), market =market):
                    cate = JoinedCategory.objects.get(category = request.POST.get('cat'), market =market)
                    no   = cate.number + 1
                    JoinedCategory.objects.filter(category = request.POST.get('cat'), market =market).update(number =no)
                    market.joiners.add(userrequested)
                    market.requesters.remove(userrequested)
                    action = 'accepted your request to join'
                    Notify.objects.create(from_user = request.user, to_user = userrequested, action = action, what = market.name, what_id = market.id )
                    
                else:
                    JoinedCategory.objects.create(business = userrequested.business, market =market, category = userrequested.business.Cate.name, number=1)
                    market.joiners.add(userrequested)
                    market.requesters.remove(userrequested)
                    action = 'accepted your request to join'
                    Notify.objects.create(from_user = request.user, to_user = userrequested, action = action, what = market.name, what_id = market.id )
                if request.is_ajax():
                    html = render_to_string(template_name ='blog/accept.html', context ={'market': market})
                    data ={'viewhtmlb': html}
                    return JsonResponse(data=data, safe=False)
            return HttpResponse('')

        if request.POST.get('idx'):
            userrequested = get_object_or_404(User, id =request.POST.get('idx'))
            market.requesters.remove(userrequested)
            return HttpResponse('')

        subcat =request.POST.get('prodSubCat')
        catx = request.POST.get('prodcat')
        if subcat and catx:
            cat = Category.objects.get(name = catx)
            sub =PostCategory.objects.get(name = subcat, cat = cat)
            colors =sub.subcat_col.all()
            fil_colors =list()
            for i in colors:
                fil_colors.append(i)
            models =sub.subcat_mod.all()
            fil_models =list()
            for i in models:
                fil_models.append(i)
            sizes =sub.subcat_size.all()
            fil_sizes =list()
            for i in sizes:
                fil_sizes.append(i)
            if request.is_ajax():
                posts=Post.objects.filter(subcat=sub, user = business.user)
                html = render_to_string(template_name = 'blog/categoryposts.html', context = {'posts':posts, 'subcat': sub, "catx":catx, 'user':request.user, 'bs':business})
                htmlx = render_to_string(template_name = 'blog/filter.html', context = {'fil_colors':fil_colors, 'fil_models':fil_models, 'fil_sizes':fil_sizes, 'subcat': sub})
                htmlxy = render_to_string(template_name = 'blog/breadcrumb.html', context = { "catx":catx, 'business':business, 'subcat': sub})
                data_dict = {"htmlviewx1": htmlx, "htmlview": html, 'htm':htmlxy }
                return JsonResponse(data=data_dict, safe=False)
        if request.POST.get('fil_col'):
            fil =request.POST.get('fil_col')
            subcat = request.POST.get('subcategory')
            subb =PostCategory.objects.get(name = subcat)
            catx = subb.cat.name
            posts=Post.objects.filter( user = business.user, color = fil, subcat =subb)

            if request.is_ajax():
                html = render_to_string(template_name = 'blog/categoryposts.html', context = {'posts':posts,  'user':request.user, 'bs':business})
                htmlxy = render_to_string(template_name = 'blog/breadcrumb.html', context = { "catx":catx, 'business':business, 'fil':fil, 'subcat': subcat})
                data_dict = { "htmlview": html, 'htm':htmlxy }
                return JsonResponse(data=data_dict, safe=False)

        if request.POST.get('fil_mod'):
            fil =request.POST.get('fil_mod')
            subcat = request.POST.get('subcategory')
            subb =PostCategory.objects.get(name = subcat)
            catx = subb.cat.name
            posts=Post.objects.filter( user = business.user, model = fil, subcat = subb)
            if request.is_ajax():
                html = render_to_string(template_name = 'blog/categoryposts.html', context = {'posts':posts,  'user':request.user, 'bs':business})
                htmlxy = render_to_string(template_name = 'blog/breadcrumb.html', context = { "catx":catx, 'business':business, 'fil':fil, 'subcat': subcat})
                data_dict = { "htmlview": html, 'htm':htmlxy }
                return JsonResponse(data=data_dict, safe=False)

        if request.POST.get('fil_size'):
            fil =request.POST.get('fil_size')
            subcat = request.POST.get('subcategory')
            subb =PostCategory.objects.get(name = subcat)
            catx = subb.cat.name
            posts=Post.objects.filter( user = business.user, size = fil, subcat = subb)
           
            if request.is_ajax():
                html = render_to_string(template_name = 'blog/categoryposts.html', context = {'posts':posts,  'user':request.user, 'bs':business})
                htmlxy = render_to_string(template_name = 'blog/breadcrumb.html', context = { "catx":catx, 'business':business, 'fil':fil, 'subcat': subcat})
                data_dict = { "htmlview": html, 'htm':htmlxy }
                return JsonResponse(data=data_dict, safe=False)

        if request.POST.get('BusinessID'):
            business =get_object_or_404(Business, id=request.POST.get('BusinessID') )
            buscat = request.POST.get('BusinessCat')
            categoryx = Category.objects.filter(user=business.user)
            subcatts = PostCategory.objects.filter(user = business.user)
            posts =Post.objects.filter(user =business.user, where =market.name)
           
            if request.is_ajax():
                html = render_to_string(template_name = 'blog/categoryposts.html', context = {'posts':posts,  'user':request.user, 'bs':business})
                htmlxy = render_to_string(template_name = 'blog/breadcrumb.html', context = {  'business':business})
                #htmlxyzx = render_to_string(template_name = 'blog/categ_ajax.html', context = {  'business':business, 'category':categoryx })
                data_dict = { "htmlview1": html, 'htm':htmlxy , }
                return JsonResponse(data=data_dict, safe=False)
        

def accept_shop(request):
    userrequested = User.objects.get(id = request.POST.get('id'))
    if market.joiners.filter(id = userrequested.id).exists():
        pass
    else:
        print(userrequested)
        market.joiners.add(userrequested)
        action = 'accepted your request'
        Notify.objects.create(from_user = request.user, to_user = userrequested, action = action, what = market.name, what_id = market.id )
        JoinRequest.objects.filter(market_id = market.id, user_from = userrequested).delete()
    data ={}
    return JsonResponse(data=data, safe=False)
def accept_friend_request(request):
    if request.POST.get('Accept'):
        userx = get_object_or_404(User, id =request.POST.get('Accept'))
        Friend.objects.create(user =request.user, friend= userx)
        action = 'accepted your engagement request'
        Notify.objects.create(from_user = request.user, to_user =userx, action = action, what = userx.first_name, what_id = userx.id )
        Friend_Request.objects.filter(user = userx, to = request.user).delete()
        context={}
        return JsonResponse(context, safe= False)
def send_friend_request(request):
    if request.method =="POST":
        if request.POST.get('id'):
            user = get_object_or_404(User, id =request.POST.get('id'))
            action = 'sent an engagement request'
            fre_reqs = Friend_Request.objects.filter(user = request.user, to = user)
            users=User.objects.all()
            users_in_friend_request =list()
            if not fre_reqs:
                Notify.objects.create(from_user = request.user, to_user =user, action = action, what = user.first_name, what_id = user.id )
                Friend_Request.objects.create(user = request.user, to = user)
                for i in fre_reqs:
                    try:
                        users_in_friend_request.append(i.to_id)
                        print('create')
                    except AttributeError:
                        pass
            elif  fre_reqs:
                print('voila')
                Friend_Request.objects.filter(user = request.user, to = user).delete()
            context ={ 'is_sent': user.username}
            return JsonResponse(context, safe= False)
        if request.POST.get('user_id'):
            friend = get_object_or_404(User, id =request.POST.get('user_id'))
            print(friend)
            user =request.user
            friend_suggestion.objects.filter(friend = friend, user = user).update(status ='no show')
            return HttpResponse("")
        
    return HttpResponse("")
def send_join_market_request(request):
    market = get_object_or_404(Market, id =request.POST.get('id'))
    action = 'sent a request to join'
    if request.is_ajax():
        is_sent_join =False

        if market.requesters.filter(id=request.user.id).exists():
            is_sent_join =False
            market.requesters.remove(request.user)
            Notify.objects.filter(from_user = request.user,  what = market.name ).delete()
        else:
            print('added')
            is_sent_join = True
            Notify.objects.create(from_user = request.user, to_user =market.user, action = action, what = market.name, what_id = market.id )
            market.requesters.add(request.user)
        html = render_to_string(template_name ='blog/join.html', context ={'is_sent_join': is_sent_join, 'm': market, 'user':request.user})
        data ={'viewhtml': html}
        return JsonResponse(data=data, safe=False)
    context={'is_sent_join':is_sent_join}
    return JsonResponse(context, safe= False)
def create_market(request):
    markets = Market.objects.all()
    businesses =Business.objects.all()
    friends =Friend.objects.filter(user = request.user)
    user_location =request.user.profile.county
    businesses_near=Business.objects.filter(county=user_location).order_by('-joined')[:10]
    if request.method == 'POST':
        if request.FILES.get('imagexx'):
            name = request.POST.get('MarketName')
            typ =  request.POST.get('customRadio')
            myfile = request.FILES.get('imagexx')
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            Market.objects.create(user = request.user, name= name, type_of_market =typ, image = filename )
            return redirect('create_market')
    return render(request, 'blog/create_market.html', context ={'markets':markets,  'businesses':businesses, 'friends':friends})

def autocomplete_refer(request):
    if request.GET.get('termx'):
        que=BusinessCategory.objects.filter(name__icontains=request.GET.get('termx'))
        name=list()
        if que:
            for n in que:
                print(n.id)
                name_of_user= n.name
                name.append(name_of_user)

        return JsonResponse(name, safe=False)
    else:
        print('fuck')
    return redirect('business_one')
def make_favourite(request):
    business=get_object_or_404(Business, id=request.POST.get('id'))
    user=request.user
    favs = Favourites.objects.all()
    if request.is_ajax():
        is_favourite =False
        if business.user.id == user.id:
            pass
        else:
            if Favourites.objects.filter(user = user, bus=business):
                print('removed: ',  request.POST.get('id'))
                is_favourite =False
                Favourites.objects.filter(user = user, bus=business).delete()
            else:
                is_favourite =True
                print('added',  request.POST.get('id'))
                Favourites.objects.create(user=user, bus=business)
                action = 'added your business to favourites'
                Notify.objects.create(from_user = request.user, to_user = business.user, action = action, what = 'favourite', what_id = business.id)

        html = render_to_string(template_name = 'blog/fav.html', context = {'is_favourite':is_favourite, 'business':business})
        data_dict = {"htmlviewcc": html}
        return JsonResponse(data=data_dict, safe=False)
    return HttpResponse('')

def refer_bazenga(request, user_id):
    user_refered=get_object_or_404(User, id=user_id)
    post=get_object_or_404(Post, id=request.POST.get('id'))

def refer_person(request):
    post=get_object_or_404(Images, id=request.POST.get('id'))
    users = User.objects.all()[:1]
    if request.POST.getlist('user_id'):
        ids =request.POST.getlist('user_id')
        for i in ids:
            use = Friend.objects.get(id=i)
            Refer_Image.objects.create(image=post, from_who=request.user, to_who=use.friend)
            post.refers.add(use.friend)
            action = 'referred your post !'
            Notify.objects.create(from_user = request.user, to_user = use.friend, action = action )
            context={}
            return JsonResponse(data=context, safe=False)

    return HttpResponse('')


def business_update(request):
    businessx =get_object_or_404(Business, user_id =request.user.id)
    business = Business.objects.filter(user_id = request.user.id)
    cates=BusinessCategory.objects.all()
    bizs =Business.objects.all()
    if request.method =="POST":
        if request.FILES.get('imagefieldxcc'):
            myfile = request.FILES.get('imagefieldxcc')
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            business.update(image = filename)
        else:

            name = request.POST.get('BusinessName')
            email = request.POST.get('EmailAddress')
            PhoneNumber1 = request.POST.get('PhoneNumber1')
            PhoneNumbe2 = request.POST.get('PhoneNumber2')
            BusinessBio = request.POST.get('BusinessBio')
            from_day = request.POST.get('days1')
            to_day = request.POST.get('days2')
            open_hr1 = request.POST.get('open_hr1')
            open_hr2 = request.POST.get('open_hr2')
            county = request.POST.get('county')
            town = request.POST.get('town')
            business.update(user = request.user,
                            phone1 = PhoneNumber1,
                            phone2= PhoneNumbe2,
                            name = name,
                            county = county,
                            town = town,
                            from_day = from_day,
                            to_day = to_day,
                            from_hr = open_hr1,
                            to_hr = open_hr2,
                            email= email,
                            bio = BusinessBio,
                            )
        return redirect('view_businessprofile', businessx.id)
def showpostsinbsprofile(request):                                                         #useless
    businessx =get_object_or_404(Business, user_id =request.user.id)
    business= Business.objects.filter(user_id = request.user.id)
    posts_byuser = Post.objects.filter(user_id =request.user.id )
    favourites=Favourites.objects.filter(bus_id=businessx.id)
    favos=Favourites.objects.filter(user=request.user)
    no_favs = favourites.count()
    no_of_pins = 0
    no_of_refers = 0
    for  ik in posts_byuser:
        no_of_pins += ik.pins.count()
        no_of_refers += ik.refer.count()
    return render(request, 'blog/posts_in_profile.html', context = {'business':business, 'favos':favos, 'posts':posts_byuser,'no_favs':no_favs, 'no_of_refers':no_of_refers, 'no_of_pins':no_of_pins, })

def view_businessprofile(request, pk):
    business=get_object_or_404(Business, pk=pk)
    userx =business.user
    bizs =Business.objects.all()
    cats=PostCategory.objects.filter(user_id=userx.id)
    favourites=Favourites.objects.filter(bus_id=pk)
    no_favs = favourites.count()
    notifs=Notify.objects.all()
    favos=Favourites.objects.filter(user=request.user)
    is_favourite=False

    no_of_pins = 0
    no_of_refers = 0
    posts_byuser = Post.objects.filter(user_id =request.user.id )
    for  ik in posts_byuser:
        no_of_pins += ik.pins.count()
        no_of_refers += ik.refer.count()
    for i in favourites:
        if i.user_id is request.user.id:
            is_favourite=True
        else:
            is_favourite=False
    return render (request, 'blog/businessprofileupdate.html', context={'business':business, 'favos':favos, 'posts':posts_byuser, 'no_of_refers':no_of_refers, 'no_of_pins':no_of_pins, 'no_favs':no_favs, 'businesses':bizs, "notifs":notifs, 'userx':userx, 'cats':cats, 'favourites':favourites, 'is_favourite':is_favourite})

def favourites_view(request):
    businesses =Business.objects.all()
    favs=Business.objects.raw
    return render(request, 'blog/favourites.html', context={'favos':bs})


def add_category(request):
    #PostCategory.objects.all().delete()
    catges = Category.objects.filter(user_id = request.user.id)
    favos=Favourites.objects.filter(user=request.user)
    notifs =Notify.objects.filter(to_user_id = request.user.id, status = 1)
    friends =Friend.objects.filter(user = request.user)
    businesses =Business.objects.all()
    if request.method=='POST':
        if request.POST.get('categoory'):
            Category.objects.create(user = request.user, name = request.POST.get('categoory'))
            return redirect('add_category')
        if request.POST.get('categoory1'):
            cat = Category.objects.get(name= request.POST.get('prodcategory'), user = request.user)
            subcat = request.POST.get('categoory1')
            
            subcat = PostCategory.objects.filter(cat = cat, user =request.user, name = request.POST.get('categoory1'))

            print(subcat)
            if subcat:
                print('Already exists')
            else:
                PostCategory.objects.create(cat = cat, user =request.user, name = request.POST.get('categoory1'))
            return redirect('add_category')

    return render(request, 'blog/category.html', context={ 'notifs':notifs, 'friends':friends, 'businesses':businesses, 'categs': catges, 'favos':favos})
def business_categs(request):
    businesses=Business.objects.all()


def categoryView(request):
    cat =request.POST.get('prodCat')
    print(cat.user)
    posts=Post.objects.filter(category=cat)
    is_liked=False
    for post in posts:
        if post.likes.filter(id=request.user.id).exists():
            is_liked =True
     
    if request.is_ajax():
        posts = Post.objects.filter(category = request.POST.get('prodCat'))
        html = render_to_string(template_name = 'blog/categoryposts.html', context = {'posts':posts, 'is_liked': is_liked})
        data_dict = {"htmlview": html}
        return JsonResponse(data=data_dict, safe=False)

    return HttpResponse('')
def CreateComment(request):
    post = get_object_or_404(Post, id = request.POST.get('id'))
    commentx = request.POST.get('comment')
    print(commentx)
    comment=Comment(author=request.user, post=post, text=commentx )
    comment.save()
    action = 'commented your post'
    Notify.objects.create(from_user = request.user, to_user =post.user, action = action, what = 'comment', what_id = comment.id )
    if request.is_ajax():
        comments = post.comments.all()
        html = render_to_string(template_name = 'blog/comment.html', context = {'post':post, 'comments': comments, 'comment':comment})
        data_dict = {"htmlviewy": html}
        return JsonResponse(data=data_dict, safe=False)
    return HttpResponse("")

def reply(request):
    form=ReplyForm()
    comment=get_object_or_404(Comment, id = request.POST.get('id'))
    rx= request.POST.get('repliedtext')
    print(rx)
    reply=Reply(author=request.user, comment=comment, text=rx )
    reply.save()
    replies=Reply.objects.filter(comment=comment)

    action = 'replied to your comment'
    Notify.objects.create(from_user = request.user, to_user =comment.author, action = action, what = 'reply', what_id = comment.id )
    if request.is_ajax():
        html = render_to_string(template_name = 'blog/reply.html', context = {'replies':replies, 'comment': comment})
        data_dict = {"htmlviewyxv": html}
        return JsonResponse(data=data_dict, safe=False)
    return HttpResponse("")


def PostDetail(request):

    post = get_object_or_404(Post, id = request.GET.get('post'))
    friends =Friend.objects.filter(user = request.user)[:5]
    url_parameter = request.GET.get("q")
    if url_parameter:
        usersx = User.objects.filter(first_name__icontains=url_parameter)
        print(usersx)
    else:
        usersx = User.objects.all()
    is_liked=False
    if post.likes.filter(id=request.user.id).exists():
        is_liked =True
    businesses =Business.objects.all()
    is_pinned=False
    for image in post.images_post.all():
        if image.pins.filter(id=request.user.id).exists():
            is_pinned=True
    if request.is_ajax():
        html = render_to_string(template_name = 'blog/art.html', context = {'usersx':usersx})
        data_dict = {"html_from_view": html}
        return JsonResponse(data=data_dict, safe=False)
   
    return render(request, 'blog/post_detail.html', context={'post':post, 'is_pinned':is_pinned,  'businesses':businesses, 'is_liked':is_liked, 'friends':friends})


class PostView(ListView):
    def get(self, request):

        users=User.objects.all()[:5]
        posts=Post.objects.filter().order_by('-created_date')
        
        businesses=Business.objects.all()
        suggested_users = friend_suggestion.objects.filter(user = request.user, status ='show')
        fre_reqs = Friend_Request.objects.filter(user = request.user)
        inco_reqs = Friend_Request.objects.filter(to= request.user)
        markets =Market.objects.all()
        #businesses_near=Business.objects.filter(Location=user_location).order_by('-joined')[:10]
        user = request.user
        bs=user.business
        user_county=user.profile.county
        user_town = user.profile.town
        markets =Market.objects.all()
        friends =Friend.objects.filter(user = request.user)[:5]
        businesses_near=Business.objects.filter(county=user_county, town =user_town).order_by('-joined')[:10]
        for user in users:
            business=Business.objects.filter(user_id=user.id)
        user=request.user
        Refrs = Refer_Image.objects.filter().order_by('-date_refered')
        for post in posts:
            commentsx = post.comments.all()
            for i in commentsx:
                pass
            is_liked =False
            if post.likes.filter(id=request.user.id).exists():
                is_liked=True
        for ma in markets:
            posts_market =Post.objects.filter(where = str(ma.id))
        images =Images.objects.all()

        url_parameter = request.GET.get("q")
        usersx={}
        if url_parameter:
            usersx = User.objects.filter(first_name__icontains=url_parameter)
            print(usersx)
            if request.is_ajax():
                html = render_to_string(template_name = 'blog/art.html', context = {'usersx':usersx})
                data_dict = {"html_from_view": html}
                return JsonResponse(data=data_dict, safe=False)
            
        context={'posts':posts, 'comments':commentsx, 'is_liked':is_liked, 'bs':bs, 'usersx':usersx, 'images':images, 'friends':friends, 'inco_reqs':inco_reqs, 'fre_reqs':fre_reqs, 'suggested_users':suggested_users, 'markets': markets, 
         "notifs":notifs,  'user':user, 'refs': Refrs, 'users':users, 'category':category, 'bs':business, 
        'businesses':businesses, 'zoners':businesses_near}
        
        return render(request, 'blog/all_post.html', context )
    
def pinned_postView(request, post_id):
    user=request.user
    post=Post.objects.get(id=post_id)
    businesses=Business.objects.all()
    return render(request, 'blog/pinned_post.html', context={'post':post, 'businesses':businesses})
def update_profile_pic(request):
    User_profile =Profile.objects.filter(user = request.user)
    print(request.FILES.get('upfile'))
    return HttpResponse('')



class MyShop(DetailView):
    def get(self, request):
        users =User.objects.all()
        user = request.user
        business=get_object_or_404(Business, pk=request.user.business.id)
        brands =Brand.objects.filter(user= user)
        
        posts= Post.objects.filter(user = request.user)
        draft =Shoutout.objects.filter(user = user, status = 'published')
        friends =Friend.objects.filter(user = user)
        businesses =Business.objects.all()
        categoryx = Category.objects.filter(user=user)
        subcatts = PostCategory.objects.filter(user = user)
        url_parameter = request.GET.get("q")
        notifs =Notify.objects.filter(to_user_id = request.user.id, status = 1)
        promotions = Promotions.objects.filter(user = user)
        posts_promoted = list()
        for v in promotions:
            posts_promoted.append(v.post)
        usersx={}
        user_county=user.profile.county
        user_town = user.profile.town
        categsx = BusinessCategory.objects.filter(county=user_county, town =user_town)
        if url_parameter:
            usersx = User.objects.filter(first_name__icontains=url_parameter)
        
        offers = Offer.objects.filter(user = user)
        return render(request, 'blog/myshop_landing_page.html', context={'business':business, 'brands':brands, 'owner':user,  'posts': posts, 'offers':offers, 'categsx':categsx, 'posts_promoted':posts_promoted, 'promotions':promotions, 'notifs':notifs, 'subcatts':subcatts, 'category':categoryx, 'users':users, 'draft':draft, 'usersx':usersx, 'bs':business, 'businesses':businesses, 'friends':friends})
    def post(self, request):
        business=get_object_or_404(Business, pk=request.user.business.id)
        subcat =request.POST.get('prodSubCat')
        catx = request.POST.get('prodcat')
        posts ={}
        fil   ={}
        if subcat and catx:
            cat = Category.objects.get(name = catx, user = business.user)
            sub =PostCategory.objects.get(name = subcat, cat = cat, user = business.user)
            colors =sub.subcat_col.all()

            fil_colors =list()
            for i in colors:
                fil_colors.append(i)
            models =sub.subcat_mod.all()
            fil_models =list()
            for i in models:
                fil_models.append(i)
            sizes =sub.subcat_size.all()
            fil_sizes =list()
            for i in sizes:
                fil_sizes.append(i)
            if request.is_ajax():
                posts=Post.objects.filter(subcat=sub, user = business.user)
                html = render_to_string(template_name = 'blog/categoryposts.html', context = {'posts':posts, 'subcat': sub, "catx":catx, 'user':request.user, 'bs':business})
                htmlx = render_to_string(template_name = 'blog/filter.html', context = {'fil_colors':fil_colors, 'fil_models':fil_models, 'fil_sizes':fil_sizes, 'subcat': sub})
                htmlxy = render_to_string(template_name = 'blog/breadcrumb.html', context = { "catx":catx, 'business':business, 'subcat': sub})
                data_dict = {"htmlviewx1": htmlx, "htmlview": html, 'htm':htmlxy }
                return JsonResponse(data=data_dict, safe=False)
        if request.POST.get('fil_col'):
            fil =request.POST.get('fil_col')
            subcat = request.POST.get('subcategory')
            cat = Category.objects.get(name = request.POST.get('cat_name'), user = business.user)
            subb =PostCategory.objects.get(name = subcat,cat =cat, user = business.user)
            catx = subb.cat.name
            posts=Post.objects.filter( user = business.user, color = fil, subcat =subb)
        if request.POST.get('fil_mod'):
            fil =request.POST.get('fil_mod')
            subcat = request.POST.get('subcategory')
            cat = Category.objects.get(name = request.POST.get('cat_name'), user = business.user)
            subb =PostCategory.objects.get(name = subcat,cat =cat, user = business.user)
            catx = subb.cat.name
            posts=Post.objects.filter( user = business.user, model = fil, subcat = subb)
        if request.POST.get('fil_size'):
            fil =request.POST.get('fil_size')
            subcat = request.POST.get('subcategory')
            cat = Category.objects.get(name = request.POST.get('cat_name'),                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            user = business.user)
            subb =PostCategory.objects.get(name = subcat,cat =cat, user = business.user)
            catx = subb.cat.name
            posts=Post.objects.filter( user = business.user, size = fil, subcat = subb)
            for p in posts:
                catx= p.subcat.cat.name
                subcat =p.subcat.name
        if request.POST.get('offerName'):
            post =get_object_or_404(Post, id = request.POST.get('promo_id'))
        if request.POST.get('post_id'):
            post=get_object_or_404(Post, pk=request.POST.get('post_id'))
            post.delete()

        if request.is_ajax():
            htmly = render_to_string(template_name = 'blog/myshop_landing_page.html', context = {'posts':posts, 'draft':{}, 'user':request.user, 'bs':business})
            html = render_to_string(template_name = 'blog/categoryposts.html', context = {'posts':posts,  'user':request.user, 'bs':business})
            htmlxy = render_to_string(template_name = 'blog/breadcrumb.html', context = { "catx":catx, 'business':business, 'fil':fil, 'subcat': subcat})
            data_dict = { "htmlview": html, 'htm':htmlxy, "htmlf" : htmly }
            return JsonResponse(data=data_dict, safe=False)

class CategoryView(ListView):
    def post(self, request, cat):
        business=get_object_or_404(Business, pk=request.user.business.id)
        subcat =request.POST.get('prodSubCat')
        catx = request.POST.get('prodcat')
        posts ={}
        fil   ={}
        if subcat and catx:
            cat = Category.objects.get(name = catx, user = business.user)
            sub =PostCategory.objects.get(name = subcat, cat = cat, user = business.user)
            colors =sub.subcat_col.all()

            fil_colors =list()
            for i in colors:
                fil_colors.append(i)
            models =sub.subcat_mod.all()
            fil_models =list()
            for i in models:
                fil_models.append(i)
            sizes =sub.subcat_size.all()
            fil_sizes =list()
            for i in sizes:
                fil_sizes.append(i)
            if request.is_ajax():
                posts=Post.objects.filter(subcat=sub, user = business.user)
                html = render_to_string(template_name = 'blog/categoryposts.html', context = {'posts':posts, 'subcat': sub, "catx":catx, 'user':request.user, 'bs':business})
                htmlx = render_to_string(template_name = 'blog/filter.html', context = {'fil_colors':fil_colors, 'fil_models':fil_models, 'fil_sizes':fil_sizes, 'subcat': sub})
                htmlxy = render_to_string(template_name = 'blog/breadcrumb.html', context = { "catx":catx, 'business':business, 'subcat': sub})
                data_dict = {"htmlviewx1": htmlx, "htmlview": html, 'htm':htmlxy }
                return JsonResponse(data=data_dict, safe=False)
        if request.POST.get('fil_col'):
            fil =request.POST.get('fil_col')
            subcat = request.POST.get('subcategory')
            cat = Category.objects.get(name = request.POST.get('cat_name'), user = business.user)
            subb =PostCategory.objects.get(name = subcat,cat =cat, user = business.user)
            catx = subb.cat.name
            posts=Post.objects.filter( user = business.user, color = fil, subcat =subb)
        if request.POST.get('fil_mod'):
            fil =request.POST.get('fil_mod')
            subcat = request.POST.get('subcategory')
            cat = Category.objects.get(name = request.POST.get('cat_name'), user = business.user)
            subb =PostCategory.objects.get(name = subcat,cat =cat, user = business.user)
            catx = subb.cat.name
            posts=Post.objects.filter( user = business.user, model = fil, subcat = subb)
        if request.POST.get('fil_size'):
            fil =request.POST.get('fil_size')
            subcat = request.POST.get('subcategory')
            cat = Category.objects.get(name = request.POST.get('cat_name'),                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            user = business.user)
            subb =PostCategory.objects.get(name = subcat,cat =cat, user = business.user)
            catx = subb.cat.name
            posts=Post.objects.filter( user = business.user, size = fil, subcat = subb)
            for p in posts:
                catx= p.subcat.cat.name
                subcat =p.subcat.name
        if request.POST.get('offerName'):
            post =get_object_or_404(Post, id = request.POST.get('promo_id'))
        if request.POST.get('post_id'):
            post=get_object_or_404(Post, pk=request.POST.get('post_id'))
            post.delete()

        if request.is_ajax():
            htmly = render_to_string(template_name = 'blog/myshop_landing_page.html', context = {'posts':posts, 'draft':{}, 'user':request.user, 'bs':business})
            html = render_to_string(template_name = 'blog/categoryposts.html', context = {'posts':posts,  'user':request.user, 'bs':business})
            htmlxy = render_to_string(template_name = 'blog/breadcrumb.html', context = { "catx":catx, 'business':business, 'fil':fil, 'subcat': subcat})
            data_dict = { "htmlview": html, 'htm':htmlxy, "htmlf" : htmly }
            return JsonResponse(data=data_dict, safe=False)


class OfferProductPage(DetailView):
    def get(self, request, pk):                                                                                                                         
        businesses=Business.objects.all()
        categsx =BusinessCategory.objects.all()
        user = request.user
        friends =Friend.objects.filter(user = user)
        return render(request, 'blog/offerProduct.html', context={'categsx': categsx, 'notifs':notifs,  'businesses':businesses, 'friends':friends})
    def post(self, request, pk):
        post = get_object_or_404(Post, id = pk)
        offername = request.POST.get('categoryi')
        offer =get_object_or_404(Offer, name = offername, user = request.user)
        price = post.price
        disc = int(request.POST.get('discount'))
        discountedPrice = int(price) - disc
        percentageDisco = (disc * 100)/int(price)
        if not Promotions.objects.filter(post = post):
            Promotions.objects.create(post = post, offer = offer, new_price =discountedPrice, perce =round(percentageDisco, 1),  user = request.user, 
                disc = disc )
            Post.objects.filter(id = post.id).update(new_price =discountedPrice, perce =round(percentageDisco, 1), disc = disc)
          
     
        return redirect('productoffer', pk = post.id)
class VisitShop(DetailView):
    def get(self, request, pk):
        user=request.user
   
        print(pk.replace('-', ' '))
        business=get_object_or_404(Business, name=pk.replace('-', ' '))
        markets =Market.objects.all()
        userx_id =business.user_id
        userx=User.objects.get(id=userx_id)
        posts=Post.objects.filter(user=userx)
        categoryx = Category.objects.filter(user=userx)
        businesses=Business.objects.all()
        draft = Shoutout.objects.filter(user = business.user, status = 'published')
        no = business.views + 1
        categsx =BusinessCategory.objects.all()
        images =Images.objects.all()###///////////////////////////Rethink
        posts_likes =0 
        for p in posts:
            posts_likes += p.likes.count()
        if business.user == request.user:
            pass
        else:
            Business.objects.filter(name = pk).update(views = no)
            log =Visit_logs.objects.filter(business_id= business.id, user= user)
            if  log:
                log.update(user = user, business =business, no_of_posts =business.user.user_posts_drafts.count(), no_of_posts_lv = business.user.user_posts_drafts.count())
            else:
                Visit_logs.objects.create(user = user, business =business, no_of_posts =business.user.user_posts_drafts.count(), no_of_posts_lv = business.user.user_posts_drafts.count())
        user_county=user.profile.county
        user_town = user.profile.town
        markets =Market.objects.all()
        businesses_near=Business.objects.filter(county=user_county, town =user_town).order_by('-joined')[:10]
        is_liked=False
        for post in posts:
            if post.likes.filter(id=request.user.id).exists():
                is_liked =True
        is_favourite=False
        friends =Friend.objects.filter(user = user)
        if Favourites.objects.filter(user_id = user.id, bus_id = business.id):
            is_favourite =True

        carts = Cart.objects.filter(user = request.user, busi = business, status ='not placed')
        total = 0
        sub_total =0
        for g in carts:
            total += int(g.total)
            sub_total = total + 120

        promotions = Promotions.objects.filter(user = business.user)
        posts_promoted = list()
        for v in promotions:
            posts_promoted.append(v.post)
        notifs =Notify.objects.filter(to_user_id = request.user.id, status = 1)
        offers = Offer.objects.filter(user = business.user)
        latestProducts= Post.objects.filter(user = business.user)[:4]
        brands =Brand.objects.filter(user= business.user)
        return render(request, 'blog/myshop_landing_page.html', context={'business': business, 'offers':offers, 'brands':brands, 'postsLatest':latestProducts,  'no_carts':carts.count(), 'mycarts':carts, 'total':total, 'sub_total':sub_total,  'is_liked': is_liked, 'is_favourite':is_favourite, 'posts_promoted':posts_promoted, 'draft':draft, 'user':user, 'bs': business, 'friends':friends, 'images': images, 'posts_likes':posts_likes, 'categsx':categsx,  "category":categoryx, 'owner':business.user,  'posts':posts, 'businesses':businesses, 'markets':markets, 'zoners':businesses_near, 'notifs':notifs}
        )
    def post(self, request, pk):
       
        business=get_object_or_404(Business, name=pk.replace('-', ' '))
        subcat =request.POST.get('prodSubCat')
        catx = request.POST.get('prodcat')
        user = request.user
  
        post ={}
        posts ={}

        if subcat and catx:
            cat = Category.objects.get(name = catx, user = business.user)
            sub =PostCategory.objects.get(name = subcat, cat = cat, user = business.user)
            colors =sub.subcat_col.all()

            fil_colors =list()
            for i in colors:
                fil_colors.append(i)
            print(fil_colors)
            models =sub.subcat_mod.all()
            fil_models =list()
            for i in models:
                fil_models.append(i)
            sizes =sub.subcat_size.all()
            fil_sizes =list()
            for i in sizes:
                fil_sizes.append(i)
            if request.is_ajax():
                posts=Post.objects.filter(subcat=sub, user = business.user)
                print(posts)
                html = render_to_string(template_name = 'blog/categoryposts.html', context = {'posts':posts, 'subcat': sub, "catx":catx, 'user':request.user, 'bs':business})
                htmlx = render_to_string(template_name = 'blog/filter.html', context = {'fil_colors':fil_colors, 'fil_models':fil_models, 'fil_sizes':fil_sizes, 'subcat': sub})
                htmlxy = render_to_string(template_name = 'blog/breadcrumb.html', context = { "catx":catx, 'business':business, 'subcat': sub})
                data_dict = {"htmlviewx1": htmlx, "htmlview": html, 'htm':htmlxy }
                return JsonResponse(data=data_dict, safe=False)
        if request.POST.get('fil_col'):
            fil =request.POST.get('fil_col')
            subcat = request.POST.get('subcategory')
            cat = Category.objects.get(name = request.POST.get('cat_name'), user = business.user)
            subb =PostCategory.objects.get(name = subcat,cat =cat, user = business.user)
            catx = subb.cat.name
            posts=Post.objects.filter( user = business.user, color = fil, subcat =subb)
        if request.POST.get('fil_mod'):
            fil =request.POST.get('fil_mod')
            subcat = request.POST.get('subcategory')
            cat = Category.objects.get(name = request.POST.get('cat_name'), user = business.user)
            subb =PostCategory.objects.get(name = subcat,cat =cat, user = business.user)
            catx = subb.cat.name
            posts=Post.objects.filter( user = business.user, model = fil, subcat = subb)
        if request.POST.get('fil_size'):
            fil =request.POST.get('fil_size')
            subcat = request.POST.get('subcategory')
            cat = Category.objects.get(name = request.POST.get('cat_name'), user = business.user)
            subb =PostCategory.objects.get(name = subcat,cat =cat, user = business.user)
            catx = subb.cat.name
            posts=Post.objects.filter( user = business.user, size = fil, subcat = subb)
            for p in posts:
                catx= p.subcat.cat.name
                subcat =p.subcat.name
        if request.POST.get('post_idx'):

            post =get_object_or_404(Post, id = request.POST.get('post_idx'))
            try:
                cacrt =Cart.objects.get(user = user, post =post, busi = business, status ='not placed')
                no = cacrt.items
                items = no + 1
                #Cart.objects.filter(user = user, post =post, busi = business).update(items = items)
            except Exception as e:
                Cart.objects.create(user = request.user, post =post, items = 1, busi = business, unit_price = post.price, total = post.price )
            carts = Cart.objects.filter(user = request.user, busi = business, status ='not placed')
            no = carts.count()
            total = 0
            sub_total = 0
            for g in carts:
                total += int(g.total)
                sub_total = total + 120
            xc = CartHistory.objects.filter(user =user, busi = business, status ="not placed")
            if xc:
                xc.update(units = no, total_amount = sub_total, sub_total = total)
            else:
                CartHistory.objects.create(user =user, busi = business, units = no, total_amount = int(post.price ), sub_total = post.price)
            if request.is_ajax():
                html = render_to_string(template_name = 'blog/cart.html', context = {'post':post, 'user':request.user})
                htmlv = render_to_string(template_name = 'blog/CartItems.html', context = {'post':post, 'user':request.user,  'mycarts':carts, 'sub_total': sub_total, 'total': total})
                htmlvxx = render_to_string(template_name = 'blog/CartHomeBtn.html', context = {'post':post, 'user':request.user, 'no_carts':carts.count(), 'business':business})   
                data_dict = { "htmlview": html, 'htmlvcc': htmlv, 'html4':htmlvxx}
                return JsonResponse(data=data_dict, safe=False)
        try:
            if request.is_ajax():
                html = render_to_string(template_name = 'blog/categoryposts.html', context = {'posts':posts,  'user':request.user, 'bs':business})
                htmlxy = render_to_string(template_name = 'blog/breadcrumb.html', context = { "catx":catx, 'business':business, 'fil':fil, 'subcat': subcat})
                data_dict = { "htmlview": html, 'htm':htmlxy }
                return JsonResponse(data=data_dict, safe=False)
        except Exception as e:
            pass    
class MyOrders(View):
    def get(self, request):
        business  = request.user.business
        carts = Cart.objects.filter(busi = request.user.business.id, status = 'placed')
        notifs =Notify.objects.filter(to_user_id = request.user.id, status = 1)
        orders ={}
        buyer =list()
        buyers=list()
        for c in carts:
            buyer.append(c.user)
            buyers  = list(set(buyer))
            for i in buyers:
                orders = Order.objects.filter(status = 'Not Done', user = i, busi = business)
        userordered = UsersOrders.objects.filter(busi = business)
        businesses=Business.objects.all()
        categsx =BusinessCategory.objects.all()
        user = request.user
        friends =Friend.objects.filter(user = user)
        que = request.GET.get('query')
        
        if que:
            userordered = UsersOrders.objects.filter(reference_icontains = que)


        context = {'business':business, 'orders':orders, "carts": carts, 'buyers':userordered, 'business':business,  'categsx': categsx, 'notifs':notifs,  'businesses':businesses, 'friends':friends}
        return render(request, 'blog/orders.html', context = context)
    def post(self, request):
        business  = request.user.business
        userordered = UsersOrders.objects.filter(busi = business)
        if request.POST.get('user_id'):
            user = request.POST.get('user_id')
            userordered = UsersOrders.objects.filter(busi = business, user = user)
            userordered.update(status ="Confirmed")
            xx = Order.objects.filter(busi = business, user = user).update(status ="Confirmed")
           
      

        return HttpResponse('')
class ProductDetailPage(MyShop):  


    def get(self, request, pk):
        post =get_object_or_404(Post, id = pk)
        category =post.subcat
        draft = Shoutout.objects.filter(user = post.user, status = 'published')
        relatedPosts = Post.objects.filter(user = post.user, subcat = category).exclude(id= post.id)
        businesses=Business.objects.all()
        categsx =BusinessCategory.objects.all()
        friends =Friend.objects.filter(user = request.user)
        context = {  'categsx': categsx, 'notifs':notifs, 'post':post, 'draft':draft, 'posts':relatedPosts, 'businesses':businesses, 'friends':friends}
        return render(request, 'blog/Product.html', context = context)
    def post(self, request, pk):
        pass
        

class MyCart(View):
    def get(self, request):
        #Cart.objects.filter().delete()
        #CartHistory.objects.filter().delete()
        #Order.objects.filter().delete()
        #UsersOrders.objects.filter().delete()
        pending= request.user.user_orders.all()
        user = request.user
        markets = Market.objects.all()
        businesses =Business.objects.all()
        notifs =Notify.objects.filter(to_user_id = request.user.id, status = 1)
        friends =Friend.objects.filter(user = request.user)
        #Notify.objects.filter(action ='accepted your request').update(action ='accepted your request to join')
        friends_ids =list()
        user_county=user.profile.county
        user_town = user.profile.town
        categsx = BusinessCategory.objects.filter(county=user_county, town =user_town)
        CartItems = user.user_carts.filter(status ='not placed')
        total = 0
        sub_total =0
        Cartshist = CartHistory.objects.filter(user =user, status ="not placed")
        business_ids = list()
        idss = list()
        carts = {}
        for i in CartItems:
            idss.append(i.busi)
            business_ids = list(set(idss))
            for j in business_ids:
                carts = j.business_carts.filter(status = "not placed")
                for g in carts:
                    total += int(g.total)
                    sub_total = total + 120
        business_list = list()
        idssx = list()
        for i in pending:
            idssx.append(i.busi)
            business_list = list(set(idssx))

        userordered = UsersOrders.objects.filter(user = user)
        context ={'markets':markets, 'friends': friends, 'businesses':businesses, 'buyers':userordered, 'business_list':business_list, 'pending_orders':pending, 'business_ids':business_ids,'carthist':Cartshist,  'mycarts':carts, 'total':total, 'sub_total':sub_total, 'categsx':categsx, 'notifs':notifs}
        return render(request, 'blog/MyCart.html', context= context)

    def post(self, request):
        Cartshist = CartHistory.objects.filter(user =request.user, status ="not placed")
        CartItems = request.user.user_carts.filter(status ='not placed')
        total = 0
        sub_total = 0
        business_ids = list()
        idss = list()
        carts = {}
        for i in CartItems:
            idss.append(i.busi)
            business_ids = list(set(idss))
            for j in business_ids:
                carts = j.business_carts.filter(status = "not placed")
                for g in carts:
                    total += int(g.total)
                    sub_total = total + 120
        
        for g in CartItems:
            total += int(g.total)
            sub_total = total + 120
        if request.POST.get('CartItem_idx'):
            cart =get_object_or_404(Cart, id = request.POST.get('CartItem_idx'))
            business =get_object_or_404(Business, id = request.POST.get('bus_id'))

            CartItems = request.user.user_carts.filter(status ='not placed', busi =business)
            for g in CartItems:
                total += int(g.total)
                sub_total = total + 120
            
            if request.POST.get('type') == 'add':
                number = cart.items + 1
                cartx  = Cart.objects.filter(id = request.POST.get('CartItem_idx'))
                cartx.update(items = number, total =  cart.unit_price * number)
                xc = CartHistory.objects.filter(user =request.user, busi = business, status ="not placed")
                xc.update(total_amount = sub_total + int(cart.unit_price), sub_total = total + int(cart.unit_price))
         
            if request.POST.get('type') == 'minus': 
                if cart.items > 0:
                    number = cart.items - 1
                    cartx  = Cart.objects.filter(id = request.POST.get('CartItem_idx'))
                    cartx.update(items = number, total =cart.unit_price * number)

                    xc = CartHistory.objects.filter(user =request.user, busi =business, status ="not placed")
                    xc.update(total_amount = sub_total - int(cart.unit_price), sub_total = total -int(cart.unit_price))
         
            carts = Cart.objects.filter(user = request.user, status ='not placed')
            
            for g in carts:
                total += int(g.total)
                sub_total = total + 120
            if request.is_ajax():
                htmlv = render_to_string(template_name = 'blog/items.html', context = {'user':request.user, 'business_ids':business_ids, 'carthist':Cartshist, 'mycarts':carts, 'no_carts':carts.count(), 'business':business, 'sub_total': sub_total, 'total': total})
                #htmlvx = render_to_string(template_name = 'blog/CartItems.html', context = {'user':request.user, 'business_ids':business_ids, 'carthist':Cartshist, 'mycarts':carts, 'no_carts':carts.count(), 'business':business, 'sub_total': sub_total, 'total': total})
                
                data_dict = { 'htmlvcc': htmlv}
                return JsonResponse(data=data_dict, safe=False)

        if request.POST.get('request_user_id'):
            carts = Cart.objects.filter(user = request.user, status ='not placed').delete()
            total = 0
            sub_total = 0
            if request.is_ajax():
                html = render_to_string(template_name = 'blog/cart.html', context = { 'user':request.user})
                htmlv = render_to_string(template_name = 'blog/CartItems.html', context = { 'user':request.user, 'sub_total': sub_total,'carthist':Cartshist, 'total': total, })
                htmlvxx = render_to_string(template_name = 'blog/CartHomeBtn.html', context = { 'user':request.user})
                data_dict = { "htmlview": html, 'htmlvcc': htmlv, 'html4':htmlvxx}
                return JsonResponse(data=data_dict, safe=False)
        if request.POST.get('Cart_user_id'):
            user = get_object_or_404(User, id = request.user.id)
            business =get_object_or_404(Business, id =request.POST.get('business_ID'))
            carts =user.user_carts.filter(status ='not placed', busi=business )
         
            for g in carts:
                total += int(g.total)
                sub_total = total + 120
            for g in carts:
                print(g, business)
                Order.objects.create(busi = business, user = user, cart = g)
                Cart.objects.filter(id = g.id).update(status = 'placed')

            firstname = user.first_name.upper()
            lastname  = user.last_name.upper()
            busname = business.name.upper()
            town = user.profile.town.upper()
            date = datetime.datetime.now()
            tot= str(total)

        
            ref_i = firstname[:2] + str(user.id) + str(date.month) + lastname[:2] + busname[:2] + str(date.day) 

            print('ref id', ref_i)

            message = ref_i +'HK'
            key = 26
            mode = 'encrypt' 
            LETTERS = ' BAFGHJKLMNCSTUVWYXZDEPQR'

            translated = ''
            for symbol in message:
                if symbol in LETTERS:
                    num = LETTERS.find(symbol) 
                    if mode == 'encrypt':
                        num = num + key
                    elif mode == 'decrypt':
                        num = num - key
                    if num >= len(LETTERS):
                        num = num - len(LETTERS)
                    elif num < 0:
                        num = num + len(LETTERS)
                    translated = translated + LETTERS[num]

                else:
                    translated = translated + symbol

            print(translated)

            UsersOrders.objects.create(user = user, busi = business, total =total, reference = translated)
            action = 'placed an order'
            Notify.objects.create(from_user = request.user, to_user =business.user, action = action )
            if request.is_ajax():
                carts =user.user_carts.filter(status ='not placed')
                html = render_to_string(template_name = 'blog/cart.html', context = { 'user':request.user})
                htmlvxx = render_to_string(template_name = 'blog/CartHomeBtn.html', context = { 'user':request.user, 'no_carts':carts.count(), 'business':business})
                htmlv = render_to_string(template_name = 'blog/CartItems.html', context = {  'business':business, 'mycarts':carts, 'carthist':Cartshist,})
                data_dict = {'htmlvccmk': htmlv}
                return JsonResponse(data=data_dict, safe=False)
            
        if request.POST.get('CartItem_id'):
            cart =get_object_or_404(Cart, id = request.POST.get('CartItem_id'))
            cart.delete()
            post = Post.objects.get(id =cart.post.id)
            business = post.user.business
            carts = Cart.objects.filter(user = request.user, busi = business, status ='not placed')
            xc = CartHistory.objects.filter(user =request.user, busi = business, status ="not placed")
            xcc = get_object_or_404(CartHistory, user =request.user, busi = business, status ="not placed") 
            if carts.count() == 0:
                xc.delete()
            xc.update(total_amount = xcc.sub_total - int(cart.total), units =UNITS - 1,  sub_total = xcc.total_amount - int(cart.total))
            if request.is_ajax():
                html = render_to_string(template_name = 'blog/cart.html', context = { 'user':request.user})
                htmlvxx = render_to_string(template_name = 'blog/CartHomeBtn.html', context = { 'user':request.user, 'no_carts':carts.count(), 'business':business})
                data_dict = {'htmlvccmk': htmlv}
                return JsonResponse(data=data_dict, safe=False)

        return redirect('mycart')
     
def alertAction(request):
    user = request.user
    notifs =Notify.objects.filter(to_user_id = request.user.id, status = 1)
    markets = Market.objects.all()
    businesses =Business.objects.all()
    friends =Friend.objects.filter(user = request.user)
    #Notify.objects.filter(action ='accepted your request').update(action ='accepted your request to join')
    friends_ids =list()
    user_county=user.profile.county
    user_town = user.profile.town
    categsx = BusinessCategory.objects.filter(county=user_county, town =user_town)
    for g in notifs:
        notification = Notify.objects.filter(id= g.id).update(status = 0)
    if request.is_ajax():
        html = render_to_string(template_name = 'blog/alertBTN.html', context = { 'user':request.user, 'notifs':notifs})
        data_dict = {'htmlvccmk': html}
        return JsonResponse(data=data_dict, safe=False)
    notifs =Notify.objects.filter(to_user_id = request.user.id)
    return render(request, 'blog/Alerts.html', context = { 'user':request.user, 'businesses':businesses, 'friends':friends, 'categsx':categsx, 'notifs':notifs})

def home_posting(request):
    form =TweetForm()
    formset=ImageForm()
    businesses=Business.objects.all()
    postcatform=PostCategoryForm()
    user = request.user
    user_county=user.profile.county
    user_town = user.profile.town
    markets =Market.objects.all()
    businesses_near=Business.objects.filter(county=user_county, town =user_town).order_by('-joined')[:10]
    context={'form':form, 'formset':formset, 'postcatform':postcatform , 'businesses':businesses, 'zoners':businesses_near, 'notifs':notifs}
    return render(request, 'blog/posting.html', context)
def about(request):
    users = User.objects.all()
    offers = Offer.objects.filter(user = request.user, id =1 )
    posts= Post.objects.filter(user = request.user)
    businesses = Business.objects.filter(user = request.user)
    draft =draft = Shoutout.objects.filter(user = request.user, status = 'published')
    return render(request, 'blog/about.html', context ={ "users": users, 'posts': posts, 'draft':draft, 'offers':offers, 'businesses':businesses})
def remove_image(request):
    ima=Post.objects.get(status='draft', user_id = request.user.id)
    image =ima.images_post.filter(id = request.POST.get('Accept'))
    context = {'ima':ima}
    image.delete()
    if request.is_ajax():
        print(request.POST.get('Accept'))
        html = render_to_string( template_name="blog/post_images.html", context={"d": ima})
        data_dict = {"html_viewxn": html}
        return JsonResponse(data=data_dict, safe=False)
    return JsonResponse(data =context, safe=False)
def delete_post_before(request):
    ima=Post.objects.get(status='draft', user_id = request.user.id)
    ima.delete()
    return redirect('blog-post_comment')
def publish(request):
    ima=Images.objects.get(pk= request.POST.get('image_id'))
    draftpost=Images.objects.filter(caption='no caption', user = request.user)
    post_id=ima.post_id
    query=request.POST.get('description')
    pro_name = request.POST.get('product_name')
    prod_price = request.POST.get('prod_price')
    discounted_pricex = request.POST.get('discounted_price')
    Images.objects.filter(id=request.POST.get('image_id')).update(caption = query, product_name =pro_name, earlier_price= prod_price, now_price =discounted_pricex)
    context ={}
    if request.is_ajax():
        html = render_to_string(
            template_name="blog/drafts.html", 
            context={"draftpost": draftpost}
        )

        data_dict = {"html_viewx": html}
        return JsonResponse(data=data_dict, safe=False)
    return JsonResponse(data =context, safe=False)
def comment_on_images(request, pk):#REMOVE
    ima=Images.objects.get(pk=pk)
    print(pk, ima.caption)
    post_id=ima.post_id
    post=Post.objects.get(id=post_id)
    businesses=Business.objects.all()
    coms=ima.imagecomments.all()
    no_of_comments=coms.count()
    user = request.user
    user_county=user.profile.county
    user_town = user.profile.town
    markets =Market.objects.all()
    businesses_near=Business.objects.filter(county=user_county, town =user_town).order_by('-joined')[:10]
    form =ImageCommentForm()
    if request.method=='POST':
        form=ImageCommentForm(request.POST)
        if form.is_valid():
            user = request.user
            text=form.cleaned_data.get('text')
            comment=ImageComment(author=user, img=ima, text=text )
            comment.save()
            action = 'commented your post'
            Notify.objects.create(from_user = request.user, to_user =post.user, action = action )
            return redirect('comment_on_images', ima.pk)
        else:
            print(form.errors)
    return render(request, 'blog/image_comment.html', context={'image':ima, 'notifs':notifs ,'form':form, 'post':post, 'coms':coms, 'zoners':businesses_near, 'no_of_comments':no_of_comments, 'businesses':businesses})

class AddProduct(DetailView):
    def get(self, request):
        categs = Category.objects.filter(user_id = request.user.id)
        businesses=Business.objects.all()
        categsx =BusinessCategory.objects.all()
        user = request.user
        user_county=user.profile.county
        user_town = user.profile.town
        markets =Market.objects.all()
        friends =Friend.objects.filter(user =user)
        businesses_near=Business.objects.filter(county=user_county, town =user_town).order_by('-joined')[:10]
        context={'markets':markets, 'categs':categs, 'categsx':categsx, 'friends':friends, 'businesses':businesses, 'zoners':businesses_near, 'notifs':notifs}
        return render(request, 'blog/posting.html',  context)


    def post(self, request):
        user =request.user
        files=request.FILES.getlist('addtionalProd_images')
        file = request.FILES.get('prod_image')
        video =request.FILES.get('prod_vid')
        try:
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
        except Exception as e:
            pass
        try:
            catv = Category.objects.get( name = request.POST.get('categoryS'), user = user)
            if request.is_ajax():
                html = render_to_string(template_name = 'blog/CategAjax.html', context = {'cat':catv})
               
                data_dict = { "view1": html}
                return JsonResponse(data=data_dict, safe=False)
        except Exception as e:
            pass
        print(request.POST.get('category'), 'heeerrrrrrrrrrreee')
        catv = Category.objects.get( name = request.POST.get('category'), user = user)
        cat =PostCategory.objects.get(user =user, name = request.POST.get('sbcategory'), cat =catv)
        if catv and cat:
            cat_instance  = Post.objects.create(
                                user = request.user,
                                price =request.POST.get('priceInput'), 
                                subcat =cat, 
                                description =request.POST.get('ProductDescription'), 
                                product_name =request.POST.get('ProductName'), 
                                
                                video =video, 
                                image =filename,  
                                where ="shop",
                                color = request.POST.get('colorInput'),
                                operation = request.POST.get('ServiceType'), 
                                model = request.POST.get('modelInput'),
                                size  = request.POST.get('sizeInput'))


            Visit_logs.objects.filter(business_id = user.business.id).update(no_of_posts = user.user_posts_drafts.count())
            if request.POST.get('colorInput'):
                try:
                    color = Color.objects.get(col = request.POST.get('colorInput'), subcat = cat)
                except Exception as e:
                    Color.objects.create(subcat = cat, number = 1, col = request.POST.get('colorInput'))
               
                else:
                    color = Color.objects.get(col = request.POST.get('colorInput'), subcat = cat)
                    number =color.number + 1
                    Color.objects.filter(col = request.POST.get('colorInput')).update(number = number)
        

            if request.POST.get('modelInput'):
                try:
                    model = Model.objects.get(mod = request.POST.get('modelInput'), subcat = cat)
                except Exception as e:
                    Model.objects.create(subcat =cat, number = 1, mod = request.POST.get('modelInput'))
                else:
                    model = Model.objects.get(mod = request.POST.get('modelInput'), subcat = cat)
                    number = model.number + 1
                    Model.objects.filter(mod = request.POST.get('modelInput')).update(number =number)
                
            if request.POST.get('sizeInput'):
                try:
                    size = Size.objects.get(size = request.POST.get('sizeInput'), subcat = cat)
                except Exception as e:
                    Size.objects.create(subcat =cat, number =1, size =request.POST.get('sizeInput'))
                else:
                    size = Size.objects.get(size = request.POST.get('sizeInput'), subcat = cat)
                    number =size.number + 1
                    Size.objects.filter(size = request.POST.get('sizeInput')).update(number =number)

                    
            action = 'added new post'
            #Notify.objects.create(from_user = request.user, to_user =0, action = action, what = 'business', what_id = user.business.id )
        for f in files:
            photo =Images.objects.create(post=cat_instance, user = request.user, image=f)

        return redirect('blog-AddProd')

def post_comment(request):
    categs = Category.objects.filter(user_id = request.user.id)
    draftpost=Post.objects.filter(status ='draft', user = request.user)
    businesses=Business.objects.all()
    user = request.user
    user_county=user.profile.county
    user_town = user.profile.town
    markets =Market.objects.all()
    businesses_near=Business.objects.filter(county=user_county, town =user_town).order_by('-joined')[:10]
    if request.method=='POST':
        files=request.FILES.getlist('addtionalProd_images')
        file = request.FILES.get('prod_image')
        video =request.FILES.get('prod_vid')
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        catv = Category.objects.get( name = request.POST.get('category'))
        no = catv.number + 1
        if Category.objects.filter(user_id = request.user.id, name = request.POST.get('category')):
            Category.objects.filter(user_id = request.user.id, name = request.POST.get('category')).update(number = no)
            cat =PostCategory.objects.get(name = request.POST.get('sbcategory'))
            cat_instance  = Post.objects.create(
                                user = request.user,
                                price =request.POST.get('priceInput'), 
                                subcat =cat, 
                                description =request.POST.get('ProductDescription'), 
                                video =video, 
                                image =filename, 
                                status = 'draft', 
                                where ="shop")
            Visit_logs.objects.filter(business_id = user.business.id).update(no_of_posts = user.user_posts_drafts.count())

            Filter.objects.create(post = cat_instance, 
                user  = request.user, 
                color = request.POST.get('colorInput'), 
                model = request.POST.get('modelInput'),
                size  = request.POST.get('sizeInput'))
            action = 'added new post'
            #Notify.objects.create(from_user = request.user, to_user =0, action = action, what = 'business', what_id = user.business.id )
        for f in files:
            photo =Images.objects.create(post=cat_instance, user = request.user, image=f)
        return redirect('blog-post_comment')
    context={'markets':markets, 'categs':categs, 'draftpost':draftpost, 'businesses':businesses, 'zoners':businesses_near, 'notifs':notifs}
    return render(request, 'blog/posting.html',  context)
def detail_post(request, pk):
    post=Post.objects.get(pk=pk)
    posts=Post.objects.all()
    business=Business.objects.get(user=post.user)
    comments=Comment.objects.filter(post=post)
    images=Images.objects.filter(post=post)
    businesses=Business.objects.all()
    form=CommentForm()
    formx=ReplyForm()
    user = request.user
    user_county=user.profile.county
    user_town = user.profile.town
    markets =Market.objects.all()
    businesses_near=Business.objects.filter(county=user_county, town =user_town).order_by('-joined')[:10]

    context={'posts':post, 'comments':comments,'form':form,'images':images,'posts':post, 'formx':formx, 'business':business}
    if request.method=='POST':
        form=CommentForm(request.POST)
        if form.is_valid() :
            user = request.user
            text=form.cleaned_data.get('text')
            comment=Comment(author=user, post=post, text=text )
            comment.save()
            action = 'commented your post'
            Notify.objects.create(from_user = request.user, to_user =post.user, action = action, what = 'comment', what_id = comment.id )

            return redirect('detail_post', pk=post.pk)
        elif formx.is_valid(): 
            user=request.user
            text=form.cleaned_data['text']
            reply=Reply(author=user, comment=commentsx, text=text)
            reply.save()
            return redirect('detail_post', pk=post.pk)
    else:
        form=CommentForm()
        context={'post':post, 'comments':comments, 'form':form, 'images':images, "notifs":notifs, 'posts':post, 'formx':formx, 'business':business, 'businesses':businesses, 'zoners':businesses_near}
    return render(request, 'blog/comments.html', context)

def Pin(request):
    post=get_object_or_404(Post, id=request.POST.get('id'))
    user_id=post.user_id
    user=User.objects.get(id=user_id)
    is_pinned=False
    if post.pins.filter(id=request.user.id).exists():
        post.pins.remove(request.user)
        PinImage.objects.filter(image = post.image, user = request.user, post = post).delete()
        is_pinned=False
        action = 'unpinned your post'
        Notify.objects.create(from_user = request.user, to_user =post.user, action = action, what = 'post', what_id = post.id )
    else:
        post.pins.add(request.user)
        PinImage.objects.create(image = post.image, user = request.user, post = post)
        is_pinned=True
        action = 'pinned your post'
        Notify.objects.create(from_user = request.user, to_user =post.user, action = action, what = 'post', what_id = post.id )
    
    if request.is_ajax():
        pins= PinImage.objects.filter(user = request.user)
        posts =list()
        for f in pins:
            posts.append(f.post)
        html = render_to_string(template_name="blog/like_section.html", context={'is_pinned': is_pinned, 'post': post, 'user': request.user})
        
        data_dict = {"htmlx_view": html,}
        return JsonResponse(data=data_dict, safe=False)

def detail_reply(request, pk):
    formz=ReplyForm()
    commentsx=Comment.objects.get(pk=pk)
    replies=Reply.objects.filter(comment=commentsx)
    businesses=Business.objects.all()
    if request.method=='POST':
        form=ReplyForm(request.POST)
        if form.is_valid():
            user=request.user
            text=form.cleaned_data['text']
            reply=Reply(author=user, comment=commentsx, text=text)
            reply.save()
            return redirect('detail_post', pk=commentsx.post.id)

    return render(request, 'blog/reply.html', context={'commentsx':commentsx, 'replies':replies, 'formz':formz, 'businesses':businesses})

def like_post1(request):
    post=get_object_or_404(Post, id=request.POST.get('id'))
    user_id=post.user_id
    user=User.objects.get(id=user_id)
    is_pinned=False
    if post.pins.filter(id=request.user.id).exists():
        post.pins.remove(request.user)
        PinImage.objects.filter(image = post.image, user = request.user, post = post).delete()
        is_pinned=False
        action = 'unpinned your post'
        Notify.objects.create(from_user = request.user, to_user =post.user, action = action, what = 'post', what_id = post.id )
    else:
        post.pins.add(request.user)
        PinImage.objects.create(image = post.image, user = request.user, post = post)
        is_pinned=True
        action = 'pinned your post'
        Notify.objects.create(from_user = request.user, to_user =post.user, action = action, what = 'post', what_id = post.id )
    
    if request.is_ajax():
        pins= PinImage.objects.filter(user = request.user)
        posts =list()
        for f in pins:
            posts.append(f.post)
        html = render_to_string(template_name="blog/like_section.html", context={'is_pinned': is_pinned, 'post': post, 'user': request.user})
        html = render_to_string(template_name="blog/like_section.html", context={'is_pinned': is_pinned, 'post': post, 'user': request.user})
        
        data_dict = {"htmlx_view": html,}
        return JsonResponse(data=data_dict, safe=False) 
def like_post(request):
    post=get_object_or_404(Post, pk=request.POST.get('id'))
    if request.is_ajax():
        is_liked=False
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            is_liked=False
        else:
            post.likes.add(request.user)
            is_liked=True
        no =post.likes.count()
        html = render_to_string(template_name="blog/like.html", context={'is_liked': is_liked, 'post': post, 'user': request.user})
        data_dict = {"html_view": html}
        return JsonResponse(data=data_dict, safe=False)
def like_Business(request):
    
    business=get_object_or_404(Business, name=request.POST.get('Business_Name'))
    if request.is_ajax():
        is_liked=False
        if business.likes.filter(id=request.user.id).exists():
            business.likes.remove(request.user)
            is_liked=False
        else:
            business.likes.add(request.user)
            is_liked=True
        no = business.likes.count()
        html = render_to_string(template_name="blog/LikeBusiness.html", context={'is_liked': is_liked, 'bs': business, 'user': request.user})
        data_dict = {"html_view": html}
        return JsonResponse(data=data_dict, safe=False)


def like_comment(request, comment_id):
    comment=get_object_or_404(Comment, pk=comment_id)
    is_com_liked=False
    if comment.likes.filter(id=request.user.id).exists():
        comment.likes.remove(request.user)
        is_com_liked=False
        return redirect('detail_post')
    else:
        comment.likes.add(request.user)
        is_com_liked=True
        return redirect('detail_post')

def post_delete(request):
    print('dkvlvnlfkvlfnv') 
    if request.POST.get('post_id'):
        print('dkvlvnlfkvlfnv')
        post=get_object_or_404(Post, pk=request.POST.get('post_id'))
        post.delete()

    return HttpResponse('')

    
