import os


def draft_document_file(instance, filename):
    """
    Generate a file path for the document draft based on the document name and user ID.
    """
    # Ensure the document name is safe for use in a file path
    document_name = instance.draft.document.document_name.replace(" ", "_").replace("/", "_")

    # Construct the file path
    return os.path.join('draft_files', document_name, instance.event_instance, filename)


def document_template_path(instance, filename):
    """
    Generate a file path for the saved document based on the document name and user ID.
    """
    # Ensure the document name is safe for use in a file path
    document_name = instance.document_name.replace(" ", "_").replace("/", "_")

    # Construct the file path
    return os.path.join('document_template', document_name, filename)