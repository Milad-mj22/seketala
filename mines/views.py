from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from .models import Mine
from .forms import MineForm

@login_required
def mine_list(request):
    city_filter = request.GET.get('city')
    
    mines = Mine.objects.all()

    if city_filter:
        mines = mines.filter(city=city_filter)

    cities = Mine.objects.values_list('city', flat=True).distinct()

    return render(request, 'mines/mine_list.html', {
        'mines': mines,
        'cities': cities,
        'selected_city': city_filter
    })

@login_required
@permission_required('mines.add_mine', raise_exception=True)
def add_mine(request):
    if request.method == 'POST':
        form = MineForm(request.POST)
        if form.is_valid():
            mine = form.save(commit=False)
            mine.created_by = request.user
            mine.save()
            return redirect('mine_list')
    else:
        form = MineForm()
    return render(request, 'mines/mine_form.html', {'form': form})

@login_required
@permission_required('mines.change_mine', raise_exception=True)
def edit_mine(request, mine_id):
    mine = get_object_or_404(Mine, pk=mine_id)
    if request.method == 'POST':
        form = MineForm(request.POST, instance=mine)
        if form.is_valid():
            form.save()
            return redirect('mine_list')
    else:
        form = MineForm(instance=mine)
    return render(request, 'mines/mine_form.html', {'form': form})



@login_required
@permission_required('mines.delete_mine', raise_exception=True)
def delete_mine(request, mine_id):
    mine = get_object_or_404(Mine, pk=mine_id)
    if request.method == 'POST':
        mine.delete()
        return redirect('mine_list')
    return render(request, 'mines/confirm_delete.html', {'mine': mine})