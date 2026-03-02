from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.db.models import Count, Q
from .models import PasswordEntry, PasswordAttachment
from .forms import PasswordEntryForm
from .decorators import require_login


def simple_login(request):
    if request.method == "POST":
        password = request.POST.get("password")
        if password == settings.MASTER_LOGIN_PASSWORD:
            request.session["logged_in"] = True
            return redirect("vault:dashboard")
        else:
            return render(request, "vault/simple_login.html", {"error": "رمز عبور اشتباه است."})
    return render(request, "vault/simple_login.html")


def simple_logout(request):
    request.session.flush()
    return redirect("vault:simple_login")


@require_login
def dashboard(request):
    total_entries = PasswordEntry.objects.count()
    per_category = (
        PasswordEntry.objects
        .values("category")
        .annotate(count=Count("id"))
    )
    recent_entries = PasswordEntry.objects.order_by("-updated_at")[:5]

    ctx = {
        "total_entries": total_entries,
        "per_category": per_category,
        "recent_entries": recent_entries,
    }
    return render(request, "vault/dashboard.html", ctx)


@require_login
def password_list(request):
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()

    entries = PasswordEntry.objects.all().order_by("category", "title")

    if q:
        entries = entries.filter(
            Q(title__icontains=q) |
            Q(system_address__icontains=q) |
            Q(username__icontains=q) |
            Q(description__icontains=q)
        )

    if category:
        entries = entries.filter(category=category)

    ctx = {
        "entries": entries,
        "q": q,
        "category": category,
    }
    return render(request, "vault/password_list.html", ctx)

@require_login
def password_create(request):
    if request.method == "POST":
        form = PasswordEntryForm(request.POST, request.FILES)
        if form.is_valid():
            entry = form.save(commit=False)

            plain_password = form.cleaned_data.get("password")
            if plain_password:
                entry.set_password(plain_password)

            entry.save()

            # Single attachment
            file = request.FILES.get("attachment")
            if file:
                PasswordAttachment.objects.create(entry=entry, file=file)

            return redirect("vault:password_list")
    else:
        form = PasswordEntryForm()

    return render(request, "vault/password_form.html", {"form": form, "mode": "create"})

@require_login
def password_edit(request, pk):
    entry = get_object_or_404(PasswordEntry, pk=pk)

    if request.method == "POST":
        form = PasswordEntryForm(request.POST, request.FILES, instance=entry)
        if form.is_valid():
            entry = form.save(commit=False)

            plain_password = form.cleaned_data.get("password")
            if plain_password:  # only change if user typed something
                entry.set_password(plain_password)

            entry.save()


            # Single attachment
            file = request.FILES.get("attachment")
            if file:
                PasswordAttachment.objects.create(entry=entry, file=file)

            return redirect("vault:password_list")
    else:
        # we do NOT show the decrypted password in the form (for safety)
        form = PasswordEntryForm(instance=entry)

    return render(request, "vault/password_form.html", {"form": form, "mode": "edit", "entry": entry})


@require_login
def password_detail(request, pk):
    entry = get_object_or_404(PasswordEntry, pk=pk)
    decrypted_password = entry.get_password()
    return render(request, "vault/password_detail.html", {
        "entry": entry,
        "password": decrypted_password,
    })
