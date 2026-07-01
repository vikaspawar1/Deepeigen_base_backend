from django.shortcuts import render

def home(request):
    data = {
        'fixed_header' : True,
        'title': 'Deep Eigen',
        'description': 'Deep Eigen is an education platform provding access to graduate level courses related to artificial intelligence and autonomous driving, with an aim to provide quality contents at a level similar to the top-universities around the world.',
        'canonical_url' : request.build_absolute_uri(request.path)
    }
    return render(request, 'home.html', data)

def faqs(request):
    data = {
        'title': 'Frequently Asked Questions | Deep Eigen',
        'description': 'List of Frequently Asked Questions.',
        'canonical_url' : request.build_absolute_uri(request.path)
    }
    return render(request, 'faqs.html', data)

def terms(request):
    data = {
        'title': 'Terms of Service | Deep Eigen',
        'description': 'Terms of Service for Deep Eigen Courses Enrollment.',
        'canonical_url' : request.build_absolute_uri(request.path)
    }
    return render(request, 'terms.html', data)

# Privacy Policy
def privacypolicy(request):
    data= {
        'title': 'Privacy Policy | Deep Eigen',
        'description': 'Deep Eigen Privacy Policy',
        'canonical_url' : request.build_absolute_uri(request.path)
    }
    return render(request, 'privacypolicy.html', data)

def privacypolicygdpr(request):
    data= {
        'title': 'Privacy Policy GDPR | Deep Eigen',
        'description': 'Deep Eigen Privacy Policy GDPR',
        'canonical_url' : request.build_absolute_uri(request.path)

    }
    return render(request, 'privacypolicygdpr.html', data)

def careers(request):
    data = {
        'title': 'Deep Eigen Careers',
        'description': 'Join our team at Deep Eigen, Explore careers for Masters, undergrads and MBA.',
        'canonical_url' : request.build_absolute_uri(request.path)
    }
    return render(request, 'careers.html', data)

# Maintenance Mode
def maintenance(request):
    data = {
        'title': 'Maintenance | Deep Eigen ',
        'description': 'Deep Eigen Maintenance Mode',
        'canonical_url' : request.build_absolute_uri(request.path)
    }
    return render(request, 'maintenance.html', data)

def robots_seo(request):
    return render(request, 'robots.txt', content_type='text')

def html_sitemap(request):
    data = {
        'title': 'Sitemap | Deep Eigen ',
        'description': 'Sitemap is a list of all the Important pages of Deep Eigen',
        'canonical_url' : request.build_absolute_uri(request.path)
    }
    return render(request, 'sitemap.html', data)

def xml_sitemap(request):
    return render(request, 'sitemap.xml', content_type='text/xml')


