from django.shortcuts import get_object_or_404, render
# Create your views here.
from django.http import HttpResponse
# views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import CustomForm, FormField, FormSubmission, FormSubmissionData
from django.contrib.auth.models import User

@login_required
def create_form(request):
    users = User.objects.all()
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST.get('description', '')
        creator_ids = request.POST.getlist('creators')
        submitter_ids = request.POST.getlist('submitters')
        form = CustomForm.objects.create(title=title, description=description, created_by=request.user)
        form.allowed_creators.set(User.objects.filter(id__in=creator_ids))
        form.allowed_submitters.set(User.objects.filter(id__in=submitter_ids))
        return redirect('add_fields', form_id=form.id)
    return render(request, 'create_form.html', {'users': users})





# @login_required
# def create_form(request):
#     if request.method == 'POST':
#         form = DynamicFormCreateForm(request.POST)
#         if form.is_valid():
#             form_instance = form.save(commit=False)
#             form_instance.created_by = request.user
#             form_instance.save()
#             form.save_m2m()
#             return redirect('add_fields', form_id=form_instance.id)
#     else:
#         form = DynamicFormCreateForm()
#     return render(request, 'forms/create_form.html', {'form': form})

@login_required
def close_form(request, form_id):
    form = get_object_or_404(CustomForm, id=form_id, created_by=request.user)
    form.is_closed = True
    form.save()
    return redirect('add_fields', form_id=form.id)









@login_required
def add_fields(request, form_id):
    form = CustomForm.objects.get(id=form_id)
    if request.method == 'POST':
        label = request.POST['label']
        field_type = request.POST['field_type']
        FormField.objects.create(form=form, label=label, field_type=field_type)
    return render(request, 'add_fields.html', {'form': form})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@login_required
@csrf_exempt
def submit_form(request, form_id):
    form = CustomForm.objects.get(id=form_id)

    if request.user not in form.allowed_submitters.all():
        return JsonResponse({"status": "error", "message": "شما اجازه ارسال این فرم را ندارید."}, status=403)

    if request.method == "POST":
        submission = FormSubmission.objects.create(form=form, submitted_by=request.user)
        for field in form.fields.all():
            value = request.POST.get(str(field.id), '')
            FormSubmissionData.objects.create(submission=submission, field=field, value=value)
        return JsonResponse({"status": "success", "message": "فرم با موفقیت ارسال شد."})

    return render(request, 'submit_form.html', {'form': form})



# views.py
from django.shortcuts import render, get_object_or_404
from .models import CustomForm, FormSubmission, FormField, FormSubmissionData

def form_results(request):
    forms = CustomForm.objects.all()
    selected_form = None
    submissions = None
    selected_submission = None
    answers = None

    form_id = request.GET.get('form')
    submission_id = request.GET.get('submission')

    if form_id:
        selected_form = get_object_or_404(CustomForm, id=form_id)
        submissions = FormSubmission.objects.filter(form=selected_form)

    if submission_id:
        selected_submission = get_object_or_404(FormSubmission, id=submission_id)
        answers = FormSubmissionData.objects.filter(submission=selected_submission)

    context = {
        'forms': forms,
        'selected_form': selected_form,
        'submissions': submissions,
        'selected_submission': selected_submission,
        'answers': answers,
    }
    return render(request, 'form_results.html', context)





# # views.py
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render

# @login_required
# def available_forms(request):
#     forms = CustomForm.objects.all()

#     return render(request, 'available_forms.html', {'forms': forms})



# views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import CustomForm

@login_required
def available_forms(request):
    all_forms = CustomForm.objects.all()

    # Add `can_submit` flag to each form for this user
    forms_with_permission = []
    for form in all_forms:
        can_submit = request.user in form.allowed_submitters.all()
        forms_with_permission.append({
            'form': form,
            'can_submit': can_submit,
        })

    return render(request, 'available_forms.html', {'forms': forms_with_permission})


