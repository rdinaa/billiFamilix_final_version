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

# gradio app to load the vector store
app1 = gr.Interface(fn=explain_code,
                    inputs=gr.Textbox(label="Insert the code segment for analysis"),
                    outputs=gr.Textbox(label="Code segment description", value=''))

# this is a placehoder for now
app2 = gr.Interface(fn=compare_code_based_on_description,
                    inputs=gr.Textbox(label="What do you want to compare"),
                    outputs=[
                        gr.Textbox(label="FAM code description", value=''),
                        gr.Textbox(label="BILLI code description", value=''),
                        gr.Textbox(label="Differences", value=''),
                        ])

# this is a placehoder for now
app3 = gr.Interface(fn=extract_code_based_on_description,
                    inputs=gr.Textbox(label="Describe piece of code are you looking for"),
                    outputs=[
                        gr.Code(label="Extracted code from BILLI", value=''),
                        gr.Code(label="Extracted code from FAM", value=''),
                        ])

app4 =  gr.Interface(fn=describe_codebase,
                    inputs=[
                        gr.Textbox(label="Input folder path"),
                        gr.Textbox(label="Description d'à qui est destiné cette documentation"),
                        gr.Textbox(label="Output folder path")
                        ],
                    outputs=[
                        gr.Textbox(label="Overall description", value=''),
                        ])

app5 =  gr.Interface(fn=compare_code,
                    inputs=[
                        gr.Textbox(label="Code FAM"),
                        gr.Textbox(label="Code BILLI"),
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
    gr.TabbedInterface([app4, app1, app5, app3, ],
                       ["Explain Codebase", "Map Codebases", "Compare Code", "Extract code"],
                       css="")
    if __name__ == "__main__":
        demo.launch(debug=True)

# demo = gr.TabbedInterface([app1, app2], ["Code Exploration", "Placeholder"])
# demo.launch()
