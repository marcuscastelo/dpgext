from dpgext import gui
from dpgext import elements as el
class MainWindow(gui.Window):
    def describe(self):
        with self:
            el.Text("Hello World!")
            el.Button().add(label="Click Me!")

class DemoGui(gui.Gui):
    def _init_windows(self):
        self.windows['main'] = MainWindow(label='Main Window')

        return super()._init_windows()

def main():
    DemoGui().run()
    pass

if __name__ == '__main__':
    main()