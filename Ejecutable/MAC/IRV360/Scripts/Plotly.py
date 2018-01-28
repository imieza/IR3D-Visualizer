import plotly
import plotly.graph_objs as go


class PrintInPlotly(object):
    def __init__(self, mainSelf, *args, **kwargs):
        self.markV, self.lineV = True, True
        self.mainSelf = mainSelf

    def markerVisible(self):
        self.markV = not self.markV

    def lineVisible(self):
        self.lineV = not self.lineV

    def filter(self, calc):
        X, Y, Z = calc['xyz']
        return [index for index,(x,y,z) in enumerate(zip(X,Y,Z)) if sum([x,y,z])]

    def plot(self, calc):
        index_filter = self.filter(calc)
        X, Y, Z = calc['xyz']
        X, Y, Z  = X[index_filter], Y[index_filter], Z[index_filter]

        time = calc["time"][calc["peaks"]][index_filter]
        x, y, z, c = [], [], [], []
        print
        for index in range(len(X)):
            x += [0,X[index], None]
            y += [0,Y[index], None]
            z += [0,Z[index], None]
            c += [time[index],time[index],None]

        lines = go.Scatter3d(
            x=x, y=y, z=z,
            line=go.Line(
                color=c,  # set color equal to a variable
                colorscale='Rainbow',
                reversescale=True,
                width=5),
            mode='lines',
            hoverinfo = "text",
            visible=True,
            hovertext=["TIme: "+str(e) for e in c],
            # colorbar = dict(
            #             title = "Millions USD")
        )
        markers = go.Scatter3d(
            x=x, y=y, z=z,
            mode='markers',
            hoverinfo = "text",
            hovertext=["TIme: "+str(e) for e in c],
            visible=True,
            marker=dict(
                size=0,
                cmax=min(c),
                cmin=max(c),
                color = c,
                colorscale = 'Rainbow',
                reversescale = True,
                colorbar = dict(title = 'Delay gap to<br> Direct Sound'),
                line=dict(color='rgb(140, 140, 170)')
            )
        )

        updatemenus = list([
            dict(type="buttons",
                 buttons=list([
                    dict(label='Lines + Markers',
                          method='restyle',
                          args=['visible', [True, True]]),
                    dict(label = 'Lines',
                         method = 'restyle',
                         args = ['visible', ["legendonly", True]]),
                    dict(label = 'Markers',
                         method = 'restyle',
                         args = ['visible', [True, False]]),
                ])
            )
        ])

        layout = dict(
            width=800,
            height=700,
            autosize=False,
            showlegend=False,
            updatemenus= updatemenus,
            opacity=0.9,
            domain=[0.55, 1],
            type='surface',
            autorange=False,
            aspectmode='manual',
            scene=dict(
                xaxis=dict(
                    range=(-1, 1),
                ),
                yaxis=dict(
                    range=(-1, 1),
                ),
                zaxis=dict(
                    range=(-1, 1),
                ),
                camera=dict(
                    up=dict(
                        x=0,
                        y=0,
                        z=1
                    ),
                    eye=dict(
                        x=-1.7428,
                        y=1.0707,
                        z=0.7100,
                    )
                ),
                aspectratio=dict(x=1, y=1, z=1)
            ),
        )

        fig = dict(data=[markers,lines], layout=layout, equal_axes=True)

        plotly.offline.plot(fig, filename=self.mainSelf.dir_path+'/Exports/'+self.mainSelf.calc["name"]+'.html', validate=False)
