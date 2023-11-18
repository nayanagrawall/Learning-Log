from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import Topic, Entry
from .forms import TopicForm, EntryForm


# Create your views here.
def index(request):
    """The home page for Learning Log"""
    return render(request, 'learning_logs/index.html')


@login_required  # This will prevent unauthenticated user to request a page protected by it. Only login user can access.
def topics(request):
    """Show all topics"""
    topics = Topic.objects.filter(owner=request.user).order_by(
        'date_added')  # filtering the topics based on the user who has added that topic
    context = {'topics': topics}
    return render(request, 'learning_logs/topics.html', context)


@login_required
def topic(request, topic_id):
    """Show a single topic and all its entries."""
    topic = Topic.objects.get(id=topic_id)
    # Make sure the topic belogs to the current user.
    if topic.owner != request.user:
        raise Http404

    entries = topic.entry_set.order_by(
        '-date_added')  # - sign in front of date_added sorts the results in reverse order
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)


@login_required
def new_topic(request):
    """Add a new topic."""
    if request.method != 'POST':
        # No data submitted; create a blank form
        form = TopicForm()
    else:
        # POST data submitted; process data.
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)  # commit False because we have to modify the new topic before saving
            new_topic.owner = request.user
            new_topic.save()
            return redirect('learning_logs:topics')  # This code will bring back the topic page after adding new topic
    # Display a blank or invalid form.
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)


@login_required
def new_entry(request, topic_id):
    """Adding a new entry for a particular topic."""
    topic = Topic.objects.get(id=topic_id)

    if topic.owner != request.user:
        raise Http404

    if request.method != 'POST':
        # No data submitted, create a blank form.
        form = EntryForm()
    else:
        # POST data submitted, process data.
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic_id)

    # display a blank or invalid form.
    context = {'topic': topic, "form": form}
    return render(request, 'learning_logs/new_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    """Edit an existing entry"""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic

    # Make sure the entry belongs to the current user
    if topic.owner != request.user:
        raise Http404  # This will display an error message.

    if request.method != 'POST':
        # Initial request; pre-fill form with the current entry.
        form = EntryForm(instance=entry)
    else:
        # POST data submitted; process data.
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)

    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)
