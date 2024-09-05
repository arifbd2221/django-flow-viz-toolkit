from django.db.models.signals import pre_save, post_save, pre_delete, post_delete

# Example signal graph addition
def add_signals_to_graph(graph, model, signal, receiver_func, signal_name):
    """
    Add a signal and its receiver to the graph.
    - signal_name is the name of the signal as a string (e.g., 'post_save', 'pre_save').
    """
    # Dereference the weak reference to get the actual receiver function
    receiver = receiver_func()  # Use .__call__() or just () to dereference

    # Ensure the receiver is valid (not garbage collected)
    if receiver is None:
        return

    # Get the name of the receiver function
    receiver_name = receiver.__name__

    # Add signal node
    graph.add_node(signal_name, label=f"Signal: {signal_name}")

    # Add receiver node
    graph.add_node(receiver_name, label=f"Receiver: {receiver_name}")

    # Connect signal to receiver
    graph.add_edge(signal_name, receiver_name)

    # Connect model to signal
    graph.add_edge(model.__name__, signal_name)


# Check model signals
def check_model_signals(graph, model):
    """
    Check for Django model signals and add them to the graph.
    """
    if hasattr(model, '_meta'):
        # Check for post_save signal
        if post_save.has_listeners(model):
            for receiver_func in post_save.receivers:
                add_signals_to_graph(graph, model, post_save, receiver_func[1], 'post_save')

        # Check for pre_save signal
        if pre_save.has_listeners(model):
            for receiver_func in pre_save.receivers:
                add_signals_to_graph(graph, model, pre_save, receiver_func[1], 'pre_save')

        # Check for post_delete signal
        if post_delete.has_listeners(model):
            for receiver_func in post_delete.receivers:
                add_signals_to_graph(graph, model, post_delete, receiver_func[1], 'post_delete')

        # Check for pre_delete signal
        if pre_delete.has_listeners(model):
            for receiver_func in pre_delete.receivers:
                add_signals_to_graph(graph, model, pre_delete, receiver_func[1], 'pre_delete')


