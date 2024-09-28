import pygame
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from tkinter import Tk, filedialog

from components.buttons import draw_button, draw_radio_button

from utils.signal_loader import SignalReader, get_signal_reader
from utils.constants import *


class ECGViewer:
    def __init__(self, window_size=1536, window_step=128):
        self.window_size = window_size
        self.window_step = window_step

        self.signal_path = None
        self.selected_reader = "apple"
        self.signal_reader = get_signal_reader(self.selected_reader)

        self.signal_generator = None
        self.current_window = None
        self.playing = False

        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("ECG Signal Viewer")

    def draw_sidebar(self):
        # Draw the sidebar area
        pygame.draw.rect(self.screen, GREY, (0, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))

        # Draw the sidebar title
        font = pygame.font.Font(None, 36)
        text_surface = font.render("Menu", True, BLACK)
        self.screen.blit(text_surface, (20, 20))

        # Draw the sidebar border
        pygame.draw.line(self.screen, BLACK, (SIDEBAR_WIDTH, 0), (SIDEBAR_WIDTH, SCREEN_HEIGHT), 2)

        # Add "Open Signal" button
        open_button_rect = pygame.Rect(20, 80, 160, 40)
        draw_button(self.screen, open_button_rect, BLUE, "Open Signal", BUTTON_FONT, WHITE)

        # Add "Close Signal" button
        close_button_rect = pygame.Rect(20, 130, 160, 40)
        draw_button(self.screen, close_button_rect, RED, "Close Signal", BUTTON_FONT, WHITE)

        # Draw radio buttons for selecting reader
        apple_reader_text = BUTTON_FONT.render("Apple Watch Reader", True, BLACK)
        physionet_reader_text = BUTTON_FONT.render("PhysioNet Reader", True, BLACK)

        # Radio button for Apple Watch Reader
        apple_radio_rect = pygame.Rect(20, 180, 20, 20)
        draw_radio_button(self.screen,apple_radio_rect, BLACK, "Apple Watch Reader", BUTTON_FONT, BLACK, self.selected_reader == "apple")

        # Radio button for PhysioNet Reader
        physionet_radio_rect = pygame.Rect(20, 210, 20, 20)
        draw_radio_button(self.screen, physionet_radio_rect, BLACK, "PhysioNet Reader", BUTTON_FONT, BLACK, self.selected_reader == "physionet")

        # Store button and radio button rects for event handling
        self.open_button_rect = open_button_rect
        self.apple_radio_rect = apple_radio_rect
        self.physionet_radio_rect = physionet_radio_rect
        self.close_button_rect = close_button_rect

    def draw_menu(self):
        self.screen.fill(GREY)
        self.draw_sidebar()

    def draw_signal(self, window_rect):
        if not self.current_window:
            return

        # Create the matplotlib figure and axis
        fig, ax = plt.subplots(figsize=(window_rect.width / 100, window_rect.height / 100), dpi=100)
        ax.plot(self.current_window, color='blue')
        ax.set_ylim(-0.1, 1.1)  # Match the scale to the normalized signal range
        ax.set_xlim(0, len(self.current_window))
        ax.grid()
        y_ticks = np.arange(0, 1.1, 0.1)
        ax.set_yticks(y_ticks)
        ax.set_xticklabels([])

        # Draw the figure on a canvas
        canvas = FigureCanvas(fig)
        canvas.draw()

        # Get the raw RGBA data from the buffer
        raw_data = canvas.buffer_rgba()

        # Convert the raw data to a pygame surface
        size = canvas.get_width_height()
        signal_surface = pygame.image.frombuffer(raw_data, size, "RGBA")

        # Blit the surface onto the pygame screen
        self.screen.blit(signal_surface, (window_rect.left, window_rect.top))

        # Close the figure to release memory
        plt.close(fig)

    def next_frame(self):
        if self.signal_generator:
            self.current_window = next(self.signal_generator, None)

    def open_signal_file(self):
        # Open a file dialog to select a signal file
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename()
        root.update()
        root.destroy()

        if file_path:
            self.signal_path = file_path
            self.signal_generator = self.signal_reader.stream_normalized_signal(file_path, self.window_size, self.window_step)
            self.current_window = next(self.signal_generator, None)

    def update_reader(self):
        self.signal_reader = get_signal_reader(self.selected_reader)

        if self.signal_path:
            self.signal_generator = self.signal_reader.stream_normalized_signal(self.signal_path, self.window_size, self.window_step)
            self.current_window = next(self.signal_generator, None)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.open_button_rect.collidepoint(event.pos):
                self.open_signal_file()

            elif self.close_button_rect.collidepoint(event.pos):
                self.signal_path = None
                self.signal_generator = None
                self.current_window = None
                self.playing = False

            elif self.apple_radio_rect.collidepoint(event.pos):
                self.selected_reader = "apple"
                self.update_reader()

            elif self.physionet_radio_rect.collidepoint(event.pos):
                self.selected_reader = "physionet"
                self.update_reader()

    def run(self):
        clock = pygame.time.Clock()
        running = True

        # Define the signal display window dimensions
        window_rect = pygame.Rect(SIDEBAR_WIDTH + 5, SCREEN_HEIGHT * 0.05, (SCREEN_WIDTH - SIDEBAR_WIDTH) * 0.95,
                                  SCREEN_HEIGHT * 0.9)

        self.draw_menu()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.next_frame()
                    elif event.key == pygame.K_SPACE:
                        self.playing = not self.playing
                self.handle_event(event)

            if self.playing:
                self.next_frame()
                time.sleep(AUTO_DELAY_TIME)

            self.draw_menu()
            self.draw_signal(window_rect)
            pygame.display.flip()
            clock.tick(30)

        pygame.quit()


if __name__ == "__main__":
    viewer = ECGViewer()
    viewer.run()
