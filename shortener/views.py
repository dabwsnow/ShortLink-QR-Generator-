import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, F
from django.utils import timezone
from .models import Link
from .forms import LinkForm
from .qr import make_qr_image, make_qr_base64


def index_view(request):
    if request.method == "POST":
        form = LinkForm(request.POST)
        if form.is_valid():
            link = form.save(commit=False)
            custom_code = form.cleaned_data.get("custom_code")
            if custom_code:
                link.code = custom_code
            link.save()
            return redirect("shortener:info", code=link.code)
    else:
        form = LinkForm()

    recent_links = Link.objects.all()[:10]
    total_links = Link.objects.count()
    total_clicks = Link.objects.aggregate(total=Sum("clicks"))["total"] or 0

    return render(
        request,
        "index.html",
        {
            "form": form,
            "recent_links": recent_links,
            "total_links": total_links,
            "total_clicks": total_clicks,
        },
    )


def redirect_view(request, code):
    link = get_object_or_404(Link, code=code)
    Link.objects.filter(pk=link.pk).update(
        clicks=F("clicks") + 1, last_accessed=timezone.now()
    )
    return HttpResponseRedirect(link.original_url)


def info_view(request, code):
    link = get_object_or_404(Link, code=code)
    short_url = request.build_absolute_uri(
        reverse("shortener:redirect", args=[link.code])
    )
    qr_data_uri = make_qr_base64(short_url)
    return render(
        request,
        "detail.html",
        {
            "link": link,
            "short_url": short_url,
            "qr_data_uri": qr_data_uri,
        },
    )


def qr_download_view(request, code):
    link = get_object_or_404(Link, code=code)
    short_url = request.build_absolute_uri(
        reverse("shortener:redirect", args=[link.code])
    )
    buf = make_qr_image(short_url)
    response = HttpResponse(buf.getvalue(), content_type="image/png")
    response["Content-Disposition"] = f'attachment; filename="qr_{link.code}.png"'
    return response


@require_POST
def delete_link_view(request, code):
    link = get_object_or_404(Link, code=code)
    link.delete()
    return redirect("shortener:index")


@csrf_exempt
def api_links_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
        except Exception:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        original_url = data.get("original_url", "").strip()
        if not original_url:
            return JsonResponse({"error": "original_url is required"}, status=400)

        custom_code = data.get("custom_code", "").strip()
        title = data.get("title", "").strip()

        if custom_code:
            if Link.objects.filter(code=custom_code).exists():
                return JsonResponse({"error": "Code already exists"}, status=400)
            link = Link(original_url=original_url, code=custom_code, title=title)
        else:
            link = Link(original_url=original_url, title=title)

        link.save()
        short_url = request.build_absolute_uri(
            reverse("shortener:redirect", args=[link.code])
        )
        return JsonResponse(
            {
                "code": link.code,
                "original_url": link.original_url,
                "short_url": short_url,
                "title": link.title,
                "clicks": link.clicks,
                "created_at": link.created_at.isoformat(),
            },
            status=201,
        )

    links = Link.objects.all()[:50]
    payload = [
        {
            "code": l.code,
            "original_url": l.original_url,
            "short_url": request.build_absolute_uri(
                reverse("shortener:redirect", args=[l.code])
            ),
            "title": l.title,
            "clicks": l.clicks,
            "created_at": l.created_at.isoformat(),
        }
        for l in links
    ]
    return JsonResponse(payload, safe=False)


def api_link_detail_view(request, code):
    link = get_object_or_404(Link, code=code)
    short_url = request.build_absolute_uri(
        reverse("shortener:redirect", args=[link.code])
    )
    return JsonResponse(
        {
            "code": link.code,
            "original_url": link.original_url,
            "short_url": short_url,
            "title": link.title,
            "clicks": link.clicks,
            "created_at": link.created_at.isoformat(),
            "last_accessed": (
                link.last_accessed.isoformat() if link.last_accessed else None
            ),
        }
    )
