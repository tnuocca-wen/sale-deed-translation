from google.cloud import translate


def translate_text_with_glossary(
    text: str = "YOUR_TEXT_TO_TRANSLATE",
    project_id: str = "numeric-chassis-395210",
    glossary_id: str = "mal-eng-glossary",
) -> translate.TranslateTextResponse:
    """Translates a given text using a glossary.

    Args:
        text: The text to translate.
        project_id: The ID of the GCP project that owns the glossary.
        glossary_id: The ID of the glossary to use.

    Returns:
        The translated text."""
    client = translate.TranslationServiceClient()
    location = "us-central1"
    parent = f"projects/{project_id}/locations/{location}"

    glossary = client.glossary_path(
        project_id, "us-central1", glossary_id  # The location of the glossary
    )

    glossary_config = translate.TranslateTextGlossaryConfig(glossary=glossary)

    # Supported language codes: https://cloud.google.com/translate/docs/languages
    response = client.translate_text(
        request={
            "contents": [text],
            "target_language_code": "en",
            "source_language_code": "ml",
            "parent": parent,
            "glossary_config": glossary_config,
        }
    )

    print("Translated text: \n")
    for translation in response.glossary_translations:
        print(f"\t {translation.translated_text}")

    return translation.translated_text # return response.glossary_translations