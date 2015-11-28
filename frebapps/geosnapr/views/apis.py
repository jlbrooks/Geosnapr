from geosnapr.models import Image
from django.http import JsonResponse

# Error response for wrong method type
wrong_method_error = {
    'errors': [{
        'status': '405',
        'detail': 'Method not allowed'
    }]
}

def bad_format_error(msg):
    context = {
        'errors':[{
            'status': '400',
            'detai;': msg
        }]
    }

def api_upload(request):
    if request.method != "POST":
        return JsonResponse(wrong_method_error)

    data = request.POST.get('data')

    if not data:
        return JsonResponse(bad_format_error("Missing 'data' component of request"))

    api_key = data.get('api_key')

    lat = data.get('lat')
    lng = data.get('lng')
    caption = data.get('caption')

    src = data.get('src')
    src_type = data.get('type')