from tutorials.models.applications import Notification

def notifications_processor(request):
    if request.user.is_authenticated:
        notifs = Notification.objects.filter(recipient=request.user, is_read=False)
    else:
        notifs = []
    return {'notifications': notifs}
