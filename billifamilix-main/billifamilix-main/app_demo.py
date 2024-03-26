import gradio as gr
from utils.bedrock import explain_code
from utils.compare_vdb import compare_code_based_on_description, extract_code_based_on_description, compare_code
from utils.codebase_description import describe_codebase
# from utils.prompts import 





# coface colors: #00a787, #214269
theme = gr.themes.Default(primary_hue="blue").set(
    # block_title_text_color="#ffffff",
    # body_background_fill="#ffffff",
    # background_fill_primary="#ffffff",
    # block_label_text_color="#ffffff",
    border_color_primary="#02365E",
    button_primary_background_fill="#61B47C",
    button_primary_background_fill_hover="#00a787",
    button_primary_text_color="#214269",
    slider_color="#ffffff",
    block_border_color="#02365E",
    button_secondary_background_fill="#02365E",
    button_secondary_text_color="#B7B7B7"
    # body_text_color="#000000",
    # block_label_text_size=100,
    # block_label_text_weight=10,
    # block_title_text_weight=3,
)


exemple_code = """package com.tvd12.example.common;

import java.util.concurrent.ThreadLocalRandom;

public final class Randoms {
    private static final String ALPHABET_CHARS = "abcdefghijklmnopqrstuvwxyz";

    private Randoms() {}

    public static String randomAlphabetic(int length) {
        StringBuilder builder = new StringBuilder();
        for (int i = 0; i < length; ++i) {
            builder.append(ALPHABET_CHARS.charAt(ThreadLocalRandom.current().nextInt(ALPHABET_CHARS.length())));
        }
        return builder.toString();
    }
}
"""



# gradio app to load the vector store
app1 = gr.Interface(fn=explain_code,
                    inputs=gr.Textbox(label="Insérer le bout de code à analyser", value=exemple_code),
                    outputs=gr.Textbox(label="Description du code", value=''))


app5 =  gr.Interface(fn=compare_code,
                    inputs=[
                        gr.Textbox(label="Code N°1", value=exemple_code),
                        gr.Textbox(label="Code N°2", value=exemple_code),
                        ],
                    outputs=[
                        gr.Textbox(label="GAP Analysis", value=''),
                        ])


js_func = """
function refresh() {
    const url = new URL(window.location);

    if (url.searchParams.get('__theme') !== 'light') {
        url.searchParams.set('__theme', 'light');
        window.location.href = url.href;
    }
}
"""


with gr.Blocks(theme=theme,js=js_func) as demo:
    gr.TabbedInterface([app1, app5],
                       ["Explain Codebase", "Compare Code"],
                       css="")
    if __name__ == "__main__":
        demo.launch(debug=True, shared=True)

# demo = gr.TabbedInterface([app1, app2], ["Code Exploration", "Placeholder"])
# demo.launch()
