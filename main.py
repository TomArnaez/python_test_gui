from gui.gui import GUIApp
import logging

if __name__ == "__main__":
    logging.basicConfig(filename='app.log', 
                        filemode='w', 
                        level=logging.DEBUG, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    
    a = GUIApp()
    a.run_gui()