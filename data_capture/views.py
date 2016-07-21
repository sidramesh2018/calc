from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def step_1(request):
    return render(request, 'data_capture/step_1.html', {
        'step_number': 1
    })


@login_required
def step_2(request):
    return render(request, 'data_capture/step_2.html', {
        'step_number': 2
    })


@login_required
def step_3(request):
    return render(request, 'data_capture/step_3.html', {
        'step_number': 3
    })


@login_required
def step_4(request):
    return render(request, 'data_capture/step_4.html', {
        'step_number': 4
    })
