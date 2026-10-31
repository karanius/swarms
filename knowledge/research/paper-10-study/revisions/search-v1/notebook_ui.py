"""Native Jupyter widget controls; no changes to Jupyter menus, CSS or chrome."""
import html,time
import ipywidgets as widgets
from IPython.display import display,HTML
from search_engine import render_results

def show_search(engine):
    question=widgets.Textarea(value='Find audience feedback, competitor pricing and monetization pieces',description='Question:',layout=widgets.Layout(width='100%',height='70px'))
    kind=widgets.Dropdown(options=[('Explain capabilities', 'answer'),('Whole templates','template'),('Components','component'),('Connected groups','connected_group')],value='answer',description='Search:')
    limit=widgets.Dropdown(options=[3,6,10],value=3,description='Results:')
    button=widgets.Button(description='Search library',icon='search',button_style='primary')
    status=widgets.HTML(value='The index is local. Search does not execute templates or assemble instances.')
    out=widgets.Output()
    def run(_):
        button.disabled=True;status.value='Searching the recorded library…';start=time.monotonic()
        try:
            with out:
                out.clear_output(wait=True)
                if kind.value=='answer':
                    answer=engine.answer(question.value,k=limit.value)
                    for name,section in answer['sections'].items():
                        display(HTML('<h2>'+html.escape(name.title())+'</h2>'));render_results(section)
                    count=sum(len(s['results']) for s in answer['sections'].values())
                else:
                    answer=engine.search(question.value,k=limit.value,kind=kind.value);render_results(answer);count=len(answer['results'])
            status.value=f'{count} source-checked candidates returned in {time.monotonic()-start:.2f} seconds. Ranking is not a probability or compatibility guarantee.'
        except Exception as exc:
            with out:out.clear_output();print('Search could not complete:',str(exc))
            status.value='Search failed; no result is being represented as successful.'
        finally:button.disabled=False
    button.on_click(run)
    display(widgets.VBox([question,widgets.HBox([kind,limit,button]),status,out]))
    return {'question':question,'kind':kind,'limit':limit,'button':button,'output':out,'status':status,'run':run}
