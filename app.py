import pygame
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from tkinter import Tk, filedialog
import platform
import os
from typing import Optional, Generator

from components.buttons import draw_button, draw_radio_button, handle_hover_effect

from utils.signal_loader import SignalReader, get_signal_reader
from utils.tagging_helpers import TaggedSignal
from utils.constants import *


class ECGViewer:
    def __init__(self, window_size=1536, window_step=128):
        self.window_size: int = window_size
        self.window_step: int = window_step

        self.signal_path: str = None
        self.signal_name: str = ""
        self.current_position: str = ""
        self.selected_reader: str = "apple"
        self.signal_reader: SignalReader = get_signal_reader(self.selected_reader)

        # Sampling rate input defaults to 512 Hz which is used in attached signals
        self.sampling_rate_input = "512"
        self.sampling_rate_active = False

        self.algo_rmssd = ""
        self.ml_rmssd = ""

        self.signal_generator: Optional[Generator[list[float], None, None]] = None
        self.current_window: Optional[list[float]] = None
        self.playing: bool = False

        pygame.init()
        self.screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
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
        hover = handle_hover_effect(open_button_rect, pygame.mouse.get_pos())
        draw_button(self.screen, open_button_rect, LIGHT_GRAY, "Open Signal", BUTTON_FONT, WHITE, hover)

        # Add "Close Signal" button
        close_button_rect = pygame.Rect(20, 130, 160, 40)
        hover = handle_hover_effect(close_button_rect, pygame.mouse.get_pos())
        draw_button(self.screen, close_button_rect, LIGHT_GRAY, "Close Signal", BUTTON_FONT, WHITE, hover)

        # Draw radio buttons for selecting reader
        apple_radio_rect = pygame.Rect(20, 180, 20, 20)
        draw_radio_button(self.screen, apple_radio_rect, DARK_GRAY, "Apple Watch Reader", BUTTON_FONT, BLACK, self.selected_reader == "apple")

        physionet_radio_rect = pygame.Rect(20, 210, 20, 20)
        draw_radio_button(self.screen, physionet_radio_rect, DARK_GRAY, "PhysioNet Reader", BUTTON_FONT, BLACK, self.selected_reader == "physionet")

        # Add "Tag Window" button
        tag_button_rect = pygame.Rect(20, 260, 160, 40)
        hover = handle_hover_effect(tag_button_rect, pygame.mouse.get_pos())
        draw_button(self.screen, tag_button_rect, LIGHT_GRAY, "Tag Current Window", BUTTON_FONT, WHITE, hover)

        # Draw "Sampling Rate [Hz]" label
        label_surface = BUTTON_FONT.render("Sampling Rate [Hz]:", True, BLACK)
        self.screen.blit(label_surface, (20, 320))

        # Add textbox for sampling rate input
        sampling_rate_rect = pygame.Rect(20, 350, 160, 30)
        pygame.draw.rect(self.screen, WHITE, sampling_rate_rect, 2)

        # Render current value in textbox
        sampling_rate_text = BUTTON_FONT.render(self.sampling_rate_input, True, BLACK)
        self.screen.blit(sampling_rate_text, (sampling_rate_rect.x + 5, sampling_rate_rect.y + 5))

        # Store button and radio button rects for event handling
        self.open_button_rect = open_button_rect
        self.apple_radio_rect = apple_radio_rect
        self.physionet_radio_rect = physionet_radio_rect
        self.close_button_rect = close_button_rect
        self.tag_button_rect = tag_button_rect
        self.sampling_rate_rect = sampling_rate_rect

    def draw_menu(self):
        self.screen.fill(GREY)
        self.draw_sidebar()
        self.draw_signal_info()

    def draw_signal(self, window_rect):
        if not self.current_window:
            return

        # Create the matplotlib figure and axis
        fig, ax = plt.subplots(figsize=(window_rect.width / PLOT_SCALE_FACTOR, window_rect.height / PLOT_SCALE_FACTOR), dpi=100)
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
            next_window = next(self.signal_generator, None)
            
            if next_window is not None:
                self.current_window = next_window
                self.current_position = str(self.signal_reader.position_to_index())
            else:
                self.playing = False
                self.signal_reader.current_position -= self.window_step

    def open_signal_file(self):
        if platform.system() == "Darwin":
            # Use macOS specific method to open file dialog
            file_path = os.popen('osascript -e "POSIX path of (choose file)"').read().strip()
        else:
            root = Tk()
            root.withdraw()
            file_path = filedialog.askopenfilename()
            root.update()
            root.destroy()

        if file_path:
            self.signal_path = file_path
            self.signal_name = os.path.split(file_path)[-1][:-4]
            self.current_position = "0"
            self.signal_reader.configure_reader(file_path, self.window_size, self.window_step)
            self.signal_generator = self.signal_reader.stream_normalized_signal()
            self.current_window = next(self.signal_generator, None)

    def update_reader(self):
        self.signal_reader = get_signal_reader(self.selected_reader)

        if self.signal_path:
            self.signal_generator = self.signal_reader.stream_normalized_signal(self.signal_path, self.window_size, self.window_step)
            self.current_window = next(self.signal_generator, None)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.sampling_rate_rect.collidepoint(event.pos):
                self.sampling_rate_active = True
            else:
                self.sampling_rate_active = False
                if self.open_button_rect.collidepoint(event.pos):
                    try:
                        self.open_signal_file()
                    except:
                        self.close_signal()

                elif self.close_button_rect.collidepoint(event.pos):
                    self.close_signal()

                elif self.apple_radio_rect.collidepoint(event.pos):
                    self.selected_reader = "apple"
                    try:
                        self.update_reader()
                    except:
                        self.close_signal()

                elif self.physionet_radio_rect.collidepoint(event.pos):
                    self.selected_reader = "physionet"
                    try:
                        self.update_reader()
                    except:
                        self.close_signal()

                elif self.tag_button_rect.collidepoint(event.pos):
                    tagged_signal = TaggedSignal(self.current_window)
                    tagged_signal.tag_window(self.sampling_rate_input)

                    signal_name = self.signal_name

                    dir_path = os.path.join(TAGGED_SIGNALS_DIR_NAME, f"size_{self.window_size}", f"step_{self.window_step}")

                    filename = f"{signal_name}_pos_{self.current_position}.json"

                    tagged_signal.save_to_json(dir_path, filename)

        if event.type == pygame.KEYDOWN and self.sampling_rate_active:
            if event.key == pygame.K_BACKSPACE:
                self.sampling_rate_input = self.sampling_rate_input[:-1]
            elif event.unicode.isdigit():
                self.sampling_rate_input += event.unicode

    def close_signal(self):
        self.signal_path = None
        self.signal_name = ""
        self.current_position = ""
        self.signal_generator = None
        self.current_window = None
        self.playing = False
        self.signal_reader.clear_reader()

    def draw_signal_info(self):
        font = pygame.font.Font(None, 24)

        # Draw the signal name
        text_surface = font.render(f"Signal: {self.signal_name}", True, BLACK)
        self.screen.blit(text_surface, (SIDEBAR_WIDTH + 10, 5))

        # Draw the status of the signal annotation
        if self.signal_name != "":
            if os.path.exists(os.path.join(TAGGED_SIGNALS_DIR_NAME, f"size_{self.window_size}", f"step_{self.window_step}", f"{self.signal_name}_pos_{self.current_position}.json")):
                tagged_state = "Tagged"
                tagged_color = DARK_GREEN
            else:
                tagged_state = "Not tagged"
                tagged_color = RED
            
            text_surface = font.render(tagged_state, True, tagged_color)
            self.screen.blit(text_surface, (SCREEN_WIDTH * 0.5, 5))

        # Draw the current window position
        text_surface = font.render(f"Window number: {self.current_position}", True, BLACK)
        self.screen.blit(text_surface, (SCREEN_WIDTH * 0.8, 5))


        # Draw the classic RMSSD value
        text_surface = font.render(f"Classic RMSSD: {self.algo_rmssd}", True, BLACK)
        self.screen.blit(text_surface, (SIDEBAR_WIDTH + 10, SCREEN_HEIGHT - 15))

        # Draw the ML RMSSD value
        text_surface = font.render(f"ML RMSSD: {self.ml_rmssd}", True, BLACK)
        self.screen.blit(text_surface, (SCREEN_WIDTH * 0.8, SCREEN_HEIGHT - 15))

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
                    elif event.key == pygame.K_LEFT:
                        if self.current_position != "0":
                            self.signal_reader.go_back()
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
