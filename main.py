import random
import time
import threading

import pandas as pd
import pygame
import sys
import os
import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox
from matplotlib import pyplot as plt

ROOT = tk.Tk()
ROOT.withdraw()
defaultGreenQ = [10, 10, 10, 10]
# Ask for simulation time
simulationTime = simpledialog.askinteger("Simulation", "Enter simulation time in seconds: ", parent=ROOT)
timePeriod = simpledialog.askinteger("Simulation", "Enter time period for data write to the file: ", parent=ROOT)

intelligentMode = messagebox.askyesno("Simulation", "Do you want intelligent traffic mode?\n\n" +
                                    "Yes: Signals respond to stopped vehicle counts\n" +
                                    "No: Simple round-robin with skipping empty lanes")
# ask for random green signal timer
randomGreenSignalTimer = True
if not intelligentMode:
    randomGreenSignalTimer = messagebox.askyesno("Simulation", "Do you want random green signal timer?")
if not randomGreenSignalTimer:
    # Ask for green signal timer
    defaultGreenQ[0] = simpledialog.askinteger("Simulation", "Enter green signal timer for direction 1: ", parent=ROOT,
                                               initialvalue=10)
    defaultGreenQ[1] = simpledialog.askinteger("Simulation", "Enter green signal timer for direction 2: ", parent=ROOT,
                                                initialvalue=10)
    defaultGreenQ[2] = simpledialog.askinteger("Simulation", "Enter green signal timer for direction 3: ", parent=ROOT,
                                               initialvalue=10)
    defaultGreenQ[3] = simpledialog.askinteger("Simulation", "Enter green signal timer for direction 4: ", parent=ROOT,
                                               initialvalue=10)

# Default values of signal timers
defaultGreen = {0: defaultGreenQ[0], 1: defaultGreenQ[1], 2: defaultGreenQ[2], 3: defaultGreenQ[3]}
defaultRed = 150
defaultYellow = 5
noOfSignals = 4
signals = []
signalTexts = [None] * noOfSignals

currentGreen = 0  # Indicates which signal is green currently
nextGreen = (currentGreen + 1) % noOfSignals  # Indicates which signal will turn green next
currentYellow = 0  # Indicates whether yellow signal is on or off
avgDelay = {'right': 0, 'down': 0, 'left': 0, 'up': 0}
speeds = {'car': 2.25, 'bus': 1.8, 'truck': 1.8, 'bike': 2.5}  # average speeds of vehicles

# Coordinates of vehicles' start
x = {'right': [0, 0, 0], 'down': [755, 727, 697], 'left': [1400, 1400, 1400], 'up': [602, 627, 657]}
y = {'right': [348, 370, 398], 'down': [0, 0, 0], 'left': [498, 466, 436], 'up': [800, 800, 800]}

vehicles = {'right': {0: [], 1: [], 2: [], 'crossed': 0}, 'down': {0: [], 1: [], 2: [], 'crossed': 0},
            'left': {0: [], 1: [], 2: [], 'crossed': 0}, 'up': {0: [], 1: [], 2: [], 'crossed': 0}}
vehicleTypes = {0: 'car', 1: 'bus', 2: 'truck', 3: 'bike'}
directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}

# Coordinates of signal image, timer, and vehicle count
signalCoods = [(530, 230), (810, 230), (810, 570), (530, 570)]
signalTimerCoods = [(530, 210), (810, 210), (810, 550), (530, 550)]

# Coordinates of stop lines
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}

# Gap between vehicles
stoppingGap = 25  # stopping gap
movingGap = 25  # moving gap

# set allowed vehicle types here
allowedVehicleTypes = {'car': messagebox.askyesno("Simulation", "Do you want cars in the simulation?", parent=ROOT),
                       'bus': messagebox.askyesno("Simulation", "Do you want buses in the simulation?", parent=ROOT),
                       'truck': messagebox.askyesno("Simulation", "Do you want trucks in the simulation?", parent=ROOT),
                       'bike': messagebox.askyesno("Simulation", "Do you want bikes in the simulation?", parent=ROOT)}
allowedVehicleTypesList = []
vehiclesTurned = {'right': {1: [], 2: []}, 'down': {1: [], 2: []}, 'left': {1: [], 2: []}, 'up': {1: [], 2: []}}
vehiclesNotTurned = {'right': {1: [], 2: []}, 'down': {1: [], 2: []}, 'left': {1: [], 2: []}, 'up': {1: [], 2: []}}
rotationAngle = 3
mid = {'right': {'x': 705, 'y': 445}, 'down': {'x': 695, 'y': 450}, 'left': {'x': 695, 'y': 425},
       'up': {'x': 695, 'y': 400}}

# set random green signal time range
randomGreenSignalTimerRange = [10, 20]

timeElapsed = 0
# simulationTime = 300
timeElapsedCoods = (1100, 50)
vehicleCountTexts = ["0", "0", "0", "0"]
vehicleCountCoods = [(480, 210), (880, 210), (880, 550), (480, 550)]

# for vehicle stats
directionLeft = {'straight': 0, 'left': 0, 'right': 0}
directionRight = {'straight': 0, 'left': 0, 'right': 0}
directionUp = {'straight': 0, 'left': 0, 'right': 0}
directionDown = {'straight': 0, 'left': 0, 'right': 0}

# Stopped vehicles count
stoppedVehiclesInJunction = {'right': 0, 'down': 0, 'left': 0, 'up': 0}
stoppedVehicles = {'right': 0, 'down': 0, 'left': 0, 'up': 0}
delayTimeForStoppedVehicles = {'right': 0, 'down': 0, 'left': 0, 'up': 0}
isVehicleStopped = {0: True, 1: True, 2: True, 3: True}

# Initialize pygame
pygame.init()
simulation = pygame.sprite.Group()

# Add these to your global variables
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
PANEL_WIDTH = 300
TOTAL_WIDTH = SCREEN_WIDTH + PANEL_WIDTH

# Colors for the panel
PANEL_BACKGROUND = (40, 44, 52)
BUTTON_COLOR = (97, 175, 239)
BUTTON_HOVER = (86, 156, 214)
TEXT_COLOR = (255, 255, 255)
SLIDER_COLOR = (152, 195, 121)

# Add this global variable at the top of the file with other globals
speed_multiplier = 100  # default speed multiplier (100%)

class Button:
    def __init__(self, x, y, width, height, text, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.is_hovered = False
        self.font = pygame.font.Font(None, 24)
        
    def draw(self, screen):
        color = BUTTON_HOVER if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        text_surface = self.font.render(self.text, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()

class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.callback = callback
        self.is_dragging = False
        self.font = pygame.font.Font(None, 24)
        
    def draw(self, screen):
        # Draw background
        pygame.draw.rect(screen, (70, 70, 70), self.rect, border_radius=3)
        
        # Draw slider
        progress = (self.value - self.min_val) / (self.max_val - self.min_val)
        slider_pos = self.rect.x + (self.rect.width * progress)
        pygame.draw.circle(screen, SLIDER_COLOR, (int(slider_pos), self.rect.centery), 10)
        
        # Draw value
        text_surface = self.font.render(str(self.value), True, TEXT_COLOR)
        text_rect = text_surface.get_rect(midleft=(self.rect.right + 10, self.rect.centery))
        screen.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.is_dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging = False
        elif event.type == pygame.MOUSEMOTION and self.is_dragging:
            rel_x = event.pos[0] - self.rect.x
            progress = max(0, min(1, rel_x / self.rect.width))
            self.value = int(self.min_val + progress * (self.max_val - self.min_val))
            self.callback(self.value)

class ControlPanel:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(None, 28)
        
        # Spacing and sizing constants
        PADDING = 20
        BUTTON_HEIGHT = 40
        SLIDER_HEIGHT = 30
        SECTION_GAP = 30
        LABEL_GAP = 5
        
        # Start y position
        y_pos = PADDING
        
        # Mode button
        self.mode_button = Button(
            x + PADDING, 
            y + y_pos, 
            width - (PADDING * 2), 
            BUTTON_HEIGHT,
            "Mode: Intelligent" if intelligentMode else "Mode: Traditional",
            self.toggle_mode
        )
        
        y_pos += BUTTON_HEIGHT + SECTION_GAP
        self.sliders = []
        
        # Green time sliders
        for i, direction in enumerate(["Right", "Down", "Left", "Up"]):
            self.sliders.append(
                Slider(
                    x + PADDING, 
                    y + y_pos, 
                    width - (PADDING * 3), 
                    SLIDER_HEIGHT,
                    5, 60, defaultGreen[i],
                    lambda v, i=i: self.update_green_time(i, v)
                )
            )
            y_pos += SLIDER_HEIGHT + LABEL_GAP
            
        y_pos += SECTION_GAP
        
        # Yellow time slider
        self.yellow_slider = Slider(
            x + PADDING, 
            y + y_pos, 
            width - (PADDING * 3), 
            SLIDER_HEIGHT,
            1, 10, defaultYellow, 
            self.update_yellow_time
        )
        
        y_pos += SLIDER_HEIGHT + SECTION_GAP
        
        # Speed slider
        self.speed_slider = Slider(
            x + PADDING, 
            y + y_pos, 
            width - (PADDING * 3), 
            SLIDER_HEIGHT,
            1, 200, 100, 
            self.update_speed
        )
        
        y_pos += SLIDER_HEIGHT + SECTION_GAP
        
        # Simulation time slider
        self.time_slider = Slider(
            x + PADDING, 
            y + y_pos, 
            width - (PADDING * 3), 
            SLIDER_HEIGHT,
            60, 600, simulationTime, 
            self.update_simulation_time
        )
        
    def draw(self, screen):
        # Draw panel background
        pygame.draw.rect(screen, PANEL_BACKGROUND, self.rect)
        
        # Draw title
        title = self.font.render("Control Panel", True, TEXT_COLOR)
        screen.blit(title, (self.rect.x + 20, self.rect.y + 10))
        
        y_pos = 100  
        
        # Draw mode button
        text = self.font.render("Traffic Mode:", True, TEXT_COLOR)
        screen.blit(text, (self.rect.x + 20, self.rect.y + y_pos - 25))
        self.mode_button.rect.y = self.rect.y + y_pos  # Update button position
        self.mode_button.draw(screen)
        
        y_pos += 60  # Gap after button
        
        # Draw green time sliders with labels
        for i, direction in enumerate(["Right", "Down", "Left", "Up"]):
            # Draw label above slider
            text = self.font.render(f"{direction} Green:", True, TEXT_COLOR)
            text_rect = text.get_rect(x=self.rect.x + 20, y=self.rect.y + y_pos)
            screen.blit(text, text_rect)
            
            # Draw slider below label
            self.sliders[i].rect.y = self.rect.y + y_pos + 25  # Position slider below text
            self.sliders[i].draw(screen)
            
            y_pos += 60  # Space for next slider group
        
        # Draw yellow time slider
        text = self.font.render("Yellow Time:", True, TEXT_COLOR)
        text_rect = text.get_rect(x=self.rect.x + 20, y=self.rect.y + y_pos)
        screen.blit(text, text_rect)
        
        self.yellow_slider.rect.y = self.rect.y + y_pos + 25
        self.yellow_slider.draw(screen)
        
        y_pos += 60
        
        # Draw speed slider
        text = self.font.render("Speed:", True, TEXT_COLOR)
        text_rect = text.get_rect(x=self.rect.x + 20, y=self.rect.y + y_pos)
        screen.blit(text, text_rect)
        
        self.speed_slider.rect.y = self.rect.y + y_pos + 25
        self.speed_slider.draw(screen)
        
        y_pos += 60
        
        # Draw simulation time slider
        text = self.font.render("Sim Time (s):", True, TEXT_COLOR)
        text_rect = text.get_rect(x=self.rect.x + 20, y=self.rect.y + y_pos)
        screen.blit(text, text_rect)
        
        self.time_slider.rect.y = self.rect.y + y_pos + 25
        self.time_slider.draw(screen)
        
    def handle_event(self, event):
        self.mode_button.handle_event(event)
        for slider in self.sliders:
            slider.handle_event(event)
        self.yellow_slider.handle_event(event)
        self.speed_slider.handle_event(event)
        self.time_slider.handle_event(event)
        
    def toggle_mode(self):
        global intelligentMode
        intelligentMode = not intelligentMode
        self.mode_button.text = "Mode: Intelligent" if intelligentMode else "Mode: Traditional"
        
    def update_green_time(self, signal_index, value):
        global defaultGreen
        defaultGreen[signal_index] = int(value)
        # Update the current signal's green time
        signals[signal_index].green = int(value)
        
    def update_yellow_time(self, value):
        global defaultYellow
        defaultYellow = int(value)
        # Update all signals' yellow time
        for signal in signals:
            signal.yellow = defaultYellow
        
    def update_speed(self, value):
        global speed_multiplier
        speed_multiplier = value
        
    def update_simulation_time(self, value):
        global simulationTime
        simulationTime = value

class TrafficSignal:
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.signalText = ""


class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.willTurn = will_turn
        self.turned = 0
        self.rotateAngle = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        self.crossedIndex = 0
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.originalImage = pygame.image.load(path)
        self.image = pygame.image.load(path)

        if len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0:
            if direction == 'right':
                self.stop = vehicles[direction][lane][self.index - 1].stop - vehicles[direction][lane][
                    self.index - 1].image.get_rect().width - stoppingGap
                stoppedVehicles[direction] += 1  # increment stopped vehicles count
            elif direction == 'left':
                self.stop = vehicles[direction][lane][self.index - 1].stop + vehicles[direction][lane][
                    self.index - 1].image.get_rect().width + stoppingGap
                stoppedVehicles[direction] += 1  # increment stopped vehicles count
            elif direction == 'down':
                self.stop = vehicles[direction][lane][self.index - 1].stop - vehicles[direction][lane][
                    self.index - 1].image.get_rect().height - stoppingGap
                stoppedVehicles[direction] += 1  # increment stopped vehicles count
            elif direction == 'up':
                self.stop = vehicles[direction][lane][self.index - 1].stop + vehicles[direction][lane][
                    self.index - 1].image.get_rect().height + stoppingGap
                stoppedVehicles[direction] += 1  # increment stopped vehicles count
        else:
            self.stop = defaultStop[direction]

        # Set new starting and stopping coordinate
        if direction == 'right':
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] -= temp
        elif direction == 'left':
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] += temp
        elif direction == 'down':
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] -= temp
        elif direction == 'up':
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        global speed_multiplier
        actual_speed = self.speed * (speed_multiplier / 100)  # Adjust speed based on multiplier
        
        if self.direction == 'right':
            if self.crossed == 0 and self.x + self.image.get_rect().width > stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if self.willTurn == 0:
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
                    directionRight['straight'] += 1
                    print('no turn right')
            if self.willTurn == 1:
                if self.lane == 1:
                    if self.crossed == 0 or self.x + self.image.get_rect().width < stopLines[self.direction] + 40:
                        if ((self.x + self.image.get_rect().width <= self.stop or (
                                currentGreen == 0 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.x + self.image.get_rect().width < (
                                vehicles[self.direction][self.lane][self.index - 1].x - movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.x += actual_speed
                    else:
                        if self.turned == 0:
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x += 2.4
                            self.y -= 2.8
                            if self.rotateAngle == 90:
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                                print('turn right to up')
                                directionRight['left'] += 1
                        else:
                            if (self.crossedIndex == 0 or (self.y > (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].y +
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1].image.get_rect().height + movingGap))):
                                self.y -= actual_speed

                elif self.lane == 2:
                    if self.crossed == 0 or self.x + self.image.get_rect().width < mid[self.direction]['x']:
                        if ((self.x + self.image.get_rect().width <= self.stop or (
                                currentGreen == 0 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.x + self.image.get_rect().width < (
                                vehicles[self.direction][self.lane][self.index - 1].x - movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.x += actual_speed
                    else:
                        if self.turned == 0:
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x += 2
                            self.y += 1.8
                            if self.rotateAngle == 90:
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                                print('turn right to down')
                                directionRight['right'] += 1
                        else:
                            if (self.crossedIndex == 0 or ((self.y + self.image.get_rect().height) < (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].y - movingGap))):
                                self.y += actual_speed
            else:
                if self.crossed == 0:
                    if ((self.x + self.image.get_rect().width <= self.stop or (
                            currentGreen == 0 and currentYellow == 0)) and (
                            self.index == 0 or self.x + self.image.get_rect().width < (
                            vehicles[self.direction][self.lane][self.index - 1].x - movingGap))):
                        self.x += actual_speed
                else:
                    if ((self.crossedIndex == 0) or (self.x + self.image.get_rect().width < (
                            vehiclesNotTurned[self.direction][self.lane][self.crossedIndex - 1].x - movingGap))):
                        self.x += actual_speed

        elif self.direction == 'down':
            if self.crossed == 0 and self.y + self.image.get_rect().height > stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if self.willTurn == 0:
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
                    print('no trun down')
                    directionDown['straight'] += 1
            if self.willTurn == 1:
                if self.lane == 1:
                    if self.crossed == 0 or self.y + self.image.get_rect().height < stopLines[self.direction] + 50:
                        if ((self.y + self.image.get_rect().height <= self.stop or (
                                currentGreen == 1 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.y + self.image.get_rect().height < (
                                vehicles[self.direction][self.lane][self.index - 1].y - movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.y += actual_speed
                    else:
                        if self.turned == 0:
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x += 1.2
                            self.y += 1.8
                            if self.rotateAngle == 90:
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                                print('turn down to right')
                                directionDown['left'] += 1
                        else:
                            if (self.crossedIndex == 0 or ((self.x + self.image.get_rect().width) < (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].x - movingGap))):
                                self.x += actual_speed
                elif self.lane == 2:
                    if self.crossed == 0 or self.y + self.image.get_rect().height < mid[self.direction]['y']:
                        if ((self.y + self.image.get_rect().height <= self.stop or (
                                currentGreen == 1 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.y + self.image.get_rect().height < (
                                vehicles[self.direction][self.lane][self.index - 1].y - movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.y += actual_speed
                    else:
                        if self.turned == 0:
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x -= 2.5
                            self.y += 2
                            if self.rotateAngle == 90:
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                                print('down to left')
                                directionDown['right'] += 1
                        else:
                            if (self.crossedIndex == 0 or (self.x > (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].x +
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1].image.get_rect().width + movingGap))):
                                self.x -= actual_speed
            else:
                if self.crossed == 0:
                    if ((self.y + self.image.get_rect().height <= self.stop or (
                            currentGreen == 1 and currentYellow == 0)) and (
                            self.index == 0 or self.y + self.image.get_rect().height < (
                            vehicles[self.direction][self.lane][self.index - 1].y - movingGap))):
                        self.y += actual_speed
                else:
                    if ((self.crossedIndex == 0) or (self.y + self.image.get_rect().height < (
                            vehiclesNotTurned[self.direction][self.lane][self.crossedIndex - 1].y - movingGap))):
                        self.y += actual_speed
        elif self.direction == 'left':
            if self.crossed == 0 and self.x < stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if self.willTurn == 0:
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
                    print('no turn left')
                    directionLeft['straight'] += 1
            if self.willTurn == 1:
                if self.lane == 1:
                    if self.crossed == 0 or self.x > stopLines[self.direction] - 70:
                        if ((self.x >= self.stop or (
                                currentGreen == 2 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.x > (vehicles[self.direction][self.lane][self.index - 1].x +
                                                             vehicles[self.direction][self.lane][
                                                                 self.index - 1].image.get_rect().width + movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.x -= actual_speed
                    else:
                        if self.turned == 0:
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x -= 1
                            self.y += 1.2
                            if self.rotateAngle == 90:
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                                print('left to down')
                                directionLeft['left'] += 1
                        else:
                            if (self.crossedIndex == 0 or ((self.y + self.image.get_rect().height) < (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].y - movingGap))):
                                self.y += actual_speed
                elif self.lane == 2:
                    if self.crossed == 0 or self.x > mid[self.direction]['x']:
                        if ((self.x >= self.stop or (
                                currentGreen == 2 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.x > (vehicles[self.direction][self.lane][self.index - 1].x +
                                                             vehicles[self.direction][self.lane][
                                                                 self.index - 1].image.get_rect().width + movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.x -= actual_speed
                    else:
                        if self.turned == 0:
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x -= 1.8
                            self.y -= 2.5
                            if self.rotateAngle == 90:
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                                print('left to up')
                                directionLeft['right'] += 1
                        else:
                            if (self.crossedIndex == 0 or (self.y > (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].y +
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1].image.get_rect().height + movingGap))):
                                self.y -= actual_speed
            else:
                if self.crossed == 0:
                    if ((self.x >= self.stop or (currentGreen == 2 and currentYellow == 0)) and (
                            self.index == 0 or self.x > (
                            vehicles[self.direction][self.lane][self.index - 1].x + vehicles[self.direction][self.lane][
                        self.index - 1].image.get_rect().width + movingGap))):
                        self.x -= actual_speed
                else:
                    if ((self.crossedIndex == 0) or (self.x > (
                            vehiclesNotTurned[self.direction][self.lane][self.crossedIndex - 1].x +
                            vehiclesNotTurned[self.direction][self.lane][
                                self.crossedIndex - 1].image.get_rect().width + movingGap))):
                        self.x -= actual_speed
        elif self.direction == 'up':
            if self.crossed == 0 and self.y < stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if self.willTurn == 0:
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
                    directionUp['straight'] += 1
            
            if ((self.crossed == 0 and (self.y >= self.stop or (currentGreen == 3 and currentYellow == 0))) or 
                self.crossed == 1):
                if (self.index == 0 or 
                    self.y > (vehicles[self.direction][self.lane][self.index - 1].y + 
                             vehicles[self.direction][self.lane][self.index - 1].image.get_rect().height + movingGap)):
                    self.y -= actual_speed

# Initialization of signals with default values
def initialize():
    minTime = randomGreenSignalTimerRange[0]
    maxTime = randomGreenSignalTimerRange[1]
    if randomGreenSignalTimer:
        ts1 = TrafficSignal(0, defaultYellow, random.randint(minTime, maxTime))
        signals.append(ts1)
        ts2 = TrafficSignal(ts1.red + ts1.yellow + ts1.green, defaultYellow, random.randint(minTime, maxTime))
        signals.append(ts2)
        ts3 = TrafficSignal(defaultRed, defaultYellow, random.randint(minTime, maxTime))
        signals.append(ts3)
        ts4 = TrafficSignal(defaultRed, defaultYellow, random.randint(minTime, maxTime))
        signals.append(ts4)
    else:
        ts1 = TrafficSignal(0, defaultYellow, defaultGreen[0])
        signals.append(ts1)
        ts2 = TrafficSignal(ts1.yellow + ts1.green, defaultYellow, defaultGreen[1])
        signals.append(ts2)
        ts3 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[2])
        signals.append(ts3)
        ts4 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[3])
        signals.append(ts4)
    repeat()


# Print the signal timers on cmd
def printStatus():
    stoppedVehiclesInJunction = countStoppedVehicles()
    print('Stopped Vehicles in Junction:', stoppedVehiclesInJunction)
    


def repeat():
    global currentGreen, currentYellow, nextGreen

    while signals[currentGreen].green > 0:  # while the timer of current green signal is not zero
        printStatus()
        updateValues()
        isVehicleStopped[currentGreen] = False
        
        # Only check for empty lanes and skip in intelligent mode
        if intelligentMode:
            current_direction = directionNumbers[currentGreen]
            has_vehicles = False
            for lane in [0, 1, 2]:
                if len(vehicles[current_direction][lane]) > 0:
                    for vehicle in vehicles[current_direction][lane]:
                        if vehicle.crossed == 0:
                            has_vehicles = True
                            break
                if has_vehicles:
                    break
            
            # If no vehicles in current direction, skip to yellow
            if not has_vehicles:
                signals[currentGreen].green = 0
        
        time.sleep(1)
        
    currentYellow = 1  # set yellow signal on
    
    # reset stop coordinates of lanes and vehicles
    for i in range(0, 3):
        for vehicle in vehicles[directionNumbers[currentGreen]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen]]
    
    while signals[currentGreen].yellow > 0:  # while the timer of current yellow signal is not zero
        printStatus()
        updateValues()
        time.sleep(1)
    currentYellow = 0  # set yellow signal off
    isVehicleStopped[currentGreen] = True

    # reset all signal times of current signal to default/random times
    if randomGreenSignalTimer:
        signals[currentGreen].green = random.randint(randomGreenSignalTimerRange[0], randomGreenSignalTimerRange[1])
    else:
        signals[currentGreen].green = defaultGreen[currentGreen]
    signals[currentGreen].yellow = defaultYellow
    signals[currentGreen].red = defaultRed

    if intelligentMode:
        # Intelligent mode: prioritize based on stopped vehicles
        stopped_counts = countStoppedVehicles()
        max_stopped = -1
        max_direction = None
        
        # Find direction with most stopped vehicles
        for direction, count in stopped_counts.items():
            if count > max_stopped:
                max_stopped = count
                if direction == 'right':
                    max_direction = 0
                elif direction == 'down':
                    max_direction = 1
                elif direction == 'left':
                    max_direction = 2
                elif direction == 'up':
                    max_direction = 3
        
        # If there are stopped vehicles, prioritize that direction
        if max_direction is not None and max_stopped > 0:
            nextGreen = max_direction
        else:
            nextGreen = (currentGreen + 1) % noOfSignals
    else:
        # Simple mode: round-robin with empty lane checking
        found_next = False
        checked_count = 0
        next_check = (currentGreen + 1) % noOfSignals
        
        while not found_next and checked_count < noOfSignals:
            direction = directionNumbers[next_check]
            # Check if there are any vehicles in this direction
            has_vehicles = False
            for lane in [0, 1, 2]:
                if len(vehicles[direction][lane]) > 0:
                    # Check if there are any vehicles that haven't crossed yet
                    for vehicle in vehicles[direction][lane]:
                        if vehicle.crossed == 0:
                            has_vehicles = True
                            break
                if has_vehicles:
                    break
            
            if has_vehicles:
                found_next = True
                nextGreen = next_check
            else:
                next_check = (next_check + 1) % noOfSignals
                checked_count += 1
        
        # If no vehicles found in any direction, just move to next signal
        if not found_next:
            nextGreen = (currentGreen + 1) % noOfSignals
    
    currentGreen = nextGreen
    # Update red time for other signals
    signals[nextGreen].red = signals[currentGreen].yellow + signals[currentGreen].green
    repeat()



# Update values of the signal timers after every second
def updateValues():
    for i in range(0, noOfSignals):
        if i == currentGreen:
            if currentYellow == 0:
                signals[i].green -= 1
            else:
                signals[i].yellow -= 1
        else:
            signals[i].red -= 1


# For Update the time for Stopped Vehicles
def updateStoppedVehiclesTime():
    if isVehicleStopped[0]:
        delayTimeForStoppedVehicles['right'] += 1
    if isVehicleStopped[1]:
        delayTimeForStoppedVehicles['down'] += 1
    if isVehicleStopped[2]:
        delayTimeForStoppedVehicles['left'] += 1
    if isVehicleStopped[3]:
        delayTimeForStoppedVehicles['up'] += 1


# Generating vehicles in the simulation
def generateVehicles():
    while True:
        vehicle_type = random.choice(allowedVehicleTypesList)
        lane_number = random.randint(1, 2)
        will_turn = 0
        if lane_number == 1:
            temp = random.randint(0, 99)
            if temp < 40:
                will_turn = 1
        elif lane_number == 2:
            temp = random.randint(0, 99)
            if temp < 40:
                will_turn = 1
        temp = random.randint(0, 99)
        direction_number = 0
        dist = [25, 50, 75, 100]
        if temp < dist[0]:
            direction_number = 0
        elif temp < dist[1]:
            direction_number = 1
        elif temp < dist[2]:
            direction_number = 2
        elif temp < dist[3]:
            direction_number = 3
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number],
                will_turn)
        time.sleep(1)


def showStats():
    totalVehicles = 0
    print('Direction-wise Vehicle Counts')
    for i in range(0, 4):
        if signals[i] is not None:
            print('Direction', i + 1, ':', vehicles[directionNumbers[i]]['crossed'])
            totalVehicles += vehicles[directionNumbers[i]]['crossed']
    print('Direction right:', directionRight)
    print('Direction down:', directionDown)
    print('Direction left:', directionLeft)
    print('Direction up:', directionUp)
    print('Total vehicles passed:', totalVehicles)
    print('Total time:', timeElapsed)
    print('delay For Stopped Vehicle:', delayTimeForStoppedVehicles)
    print('Average delay direction wise:', {
        'Direction 1': avgDelay['right'],
        'Direction 2': avgDelay['down'],
        'Direction 3': avgDelay['left'],
        'Direction 4': avgDelay['up']})

    df = pd.DataFrame({'Direction': ['Direction 1', 'Direction 2', 'Direction 3', 'Direction 4'],
                       'Total': [vehicles[directionNumbers[0]]['crossed'], vehicles[directionNumbers[1]]['crossed'],
                                 vehicles[directionNumbers[2]]['crossed'], vehicles[directionNumbers[3]]['crossed']]
                          ,
                       'Straight': [directionRight['straight'], directionDown['straight'], directionLeft['straight'],
                                    directionUp['straight']],
                       'Left': [directionRight['left'], directionDown['left'], directionLeft['left'],
                                directionUp['left']],
                       'Right': [directionRight['right'], directionDown['right'], directionLeft['right'],
                                 directionUp['right']]})

    df.plot(x='Direction', y=['Total', 'Straight', 'Left', 'Right'], kind='bar')

    plt.xticks(rotation=0)
    plt.show()
    return totalVehicles


def showStatsDialog():
    totalVehicles = showStats()
    msg = "Direction-wise Vehicle Counts\n\nDirection 1 Vehicle Behavior \nTotal: " + str(
        vehicles[directionNumbers[0]]['crossed']) + "\nStraight: " + str(directionRight['straight']) + "\nLeft: " + str(
        directionRight['left']) + "\nRight: " + str(
        directionRight['right']) + "\n\nDirection 2 Vehicle Behavior \nTotal: " + str(
        vehicles[directionNumbers[1]]['crossed']) + "\nStraight: " + str(directionDown['straight']) + "\nLeft: " + str(
        directionDown['left']) + "\nRight: " + str(
        directionDown['right']) + "\n\nDirection 3 Vehicle Behavior \nTotal: " + str(
        vehicles[directionNumbers[2]]['crossed']) + "\nStraight: " + str(directionLeft['straight']) + "\nLeft: " + str(
        directionLeft['left']) + "\nRight: " + str(
        directionLeft['right']) + "\n\nDirection 4 Vehicle Behavior \nTotal: " + str(
        vehicles[directionNumbers[3]]['crossed']) + "\nStraight: " + str(directionUp['straight']) + "\nLeft: " + str(
        directionUp['left']) + "\nRight: " + str(directionUp['right']) + "\n\nTotal vehicles passed: " + str(
        totalVehicles) + "\nTotal time: " + str(
        timeElapsed) + "\n\nAverage delay direction wise: \nDirection 1: " + str(
        avgDelay['right']) + "\nDirection 2: " + str(
        avgDelay['down']) + "\nDirection 3: " + str(avgDelay['left']) + "\nDirection 4: " + str(
        avgDelay['up'])

    tk.messagebox.showinfo("Simulation Ended", msg, parent=ROOT)

def countStoppedVehicles():
    # Reset the counts first
    for direction in stoppedVehiclesInJunction:
        stoppedVehiclesInJunction[direction] = 0
        
    # Count all stopped vehicles in each direction
    for direction in vehicles:
        for lane in [0, 1, 2]:
            prev_vehicle = None
            for vehicle in vehicles[direction][lane]:
                if vehicle.crossed == 0:  # Only check vehicles that haven't crossed yet
                    is_stopped = False
                    
                    # Check if vehicle is stopped due to signal
                    if direction == 'right':
                        if vehicle.x + vehicle.image.get_rect().width >= vehicle.stop:
                            is_stopped = True
                    elif direction == 'down':
                        if vehicle.y + vehicle.image.get_rect().height >= vehicle.stop:
                            is_stopped = True
                    elif direction == 'left':
                        if vehicle.x <= vehicle.stop:
                            is_stopped = True
                    elif direction == 'up':
                        if vehicle.y <= vehicle.stop:
                            is_stopped = True
                    
                    # Check if vehicle is stopped due to vehicle in front
                    if prev_vehicle and prev_vehicle.crossed == 0:
                        if direction == 'right':
                            if vehicle.x + vehicle.image.get_rect().width >= (prev_vehicle.x - movingGap):
                                is_stopped = True
                        elif direction == 'down':
                            if vehicle.y + vehicle.image.get_rect().height >= (prev_vehicle.y - movingGap):
                                is_stopped = True
                        elif direction == 'left':
                            if vehicle.x <= (prev_vehicle.x + prev_vehicle.image.get_rect().width + movingGap):
                                is_stopped = True
                        elif direction == 'up':
                            if vehicle.y <= (prev_vehicle.y + prev_vehicle.image.get_rect().height + movingGap):
                                is_stopped = True
                    
                    if is_stopped:
                        stoppedVehiclesInJunction[direction] += 1
                
                prev_vehicle = vehicle
                        
    return stoppedVehiclesInJunction


# Write the stats to a file
def writeStatsToFile():
    try:
        current_time = timeElapsed
        stats = f"""
Time: {current_time}s
Direction-wise Vehicle Counts:
Right: Total={vehicles['right']['crossed']} (Straight={directionRight['straight']}, Left={directionRight['left']}, Right={directionRight['right']})
Down:  Total={vehicles['down']['crossed']} (Straight={directionDown['straight']}, Left={directionDown['left']}, Right={directionDown['right']})
Left:  Total={vehicles['left']['crossed']} (Straight={directionLeft['straight']}, Left={directionLeft['left']}, Right={directionLeft['right']})
Up:    Total={vehicles['up']['crossed']} (Straight={directionUp['straight']}, Left={directionUp['left']}, Right={directionUp['right']})

Average Delays:
Right: {avgDelay['right']:.2f}
Down:  {avgDelay['down']:.2f}
Left:  {avgDelay['left']:.2f}
Up:    {avgDelay['up']:.2f}

Stopped Vehicles:
Right: {stoppedVehicles['right']}
Down:  {stoppedVehicles['down']}
Left:  {stoppedVehicles['left']}
Up:    {stoppedVehicles['up']}
----------------------------------------
"""
        with open("simulation_stats.txt", "a") as file:
            file.write(stats)
            
    except Exception as e:
        print(f"Error writing to file: {e}")


def simTime():
    global timeElapsed, simulationTime
    last_write_time = 0
    
    while True:
        updateStoppedVehiclesTime()
        avgDelayCal()
        timeElapsed += 1
        
        # Write stats every 'timePeriod' seconds
        if timeElapsed - last_write_time >= timePeriod:
            writeStatsToFile()
            last_write_time = timeElapsed
            
        time.sleep(1)
        if timeElapsed == simulationTime:
            writeStatsToFile()  # Write final stats
            showStats()


# calculate avg delay
def avgDelayCal():
    directions = ['right', 'down', 'left', 'up']

    for direction in directions:
        print('Stopped vehicles for direction', direction, ':', stoppedVehicles[direction])
        if stoppedVehicles[direction] != 0:
            avgDelay[direction] = 0.5 * (delayTimeForStoppedVehicles[direction] / stoppedVehicles[direction])

# Plot delay time for stopped vehicles
# def plotDelayTime():
#     directions = ['right', 'down', 'left', 'up']
#     delay = [delayTimeForStoppedVehicles['right'], delayTimeForStoppedVehicles['down'],
#              delayTimeForStoppedVehicles['left'], delayTimeForStoppedVehicles['up']]
#     plt.bar(directions, delay)
#     plt.xlabel('Directions')
#     plt.ylabel('Delay Time')
#     plt.title('Delay Time for Stopped Vehicles')
#     plt.show()

# Main class for the simulation
class Main:
    global allowedVehicleTypesList
    i = 0
    for vehicleType in allowedVehicleTypes:
        if allowedVehicleTypes[vehicleType]:
            allowedVehicleTypesList.append(i)
        i += 1
    thread1 = threading.Thread(name="initialization", target=initialize, args=())  # initialization
    thread1.daemon = True
    thread1.start()

    # Colours
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Screensize
    screenWidth = 1400
    screenHeight = 800
    PANEL_WIDTH = 300
    TOTAL_WIDTH = screenWidth + PANEL_WIDTH
    screenSize = (TOTAL_WIDTH, screenHeight)
    
    # Initialize screen with total width including panel
    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("SIMULATION")

    # Create control panel
    control_panel = ControlPanel(screenWidth, 0, PANEL_WIDTH, screenHeight)

    # Setting background image i.e. image of intersection
    background = pygame.image.load('images/intersection.png')

    # Loading signal images and font
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    font = pygame.font.Font(None, 30)

    thread2 = threading.Thread(name="generateVehicles", target=generateVehicles, args=())  # Generating vehicles
    thread2.daemon = True
    thread2.start()

    thread3 = threading.Thread(name="simTime", target=simTime, args=())
    thread3.daemon = True
    thread3.start()

    clock = pygame.time.Clock()
    time_interval = 500  # 500 milliseconds == 0.5 seconds
    timer_event = pygame.USEREVENT + 1
    pygame.time.set_timer(timer_event, time_interval)
    speed_multiplier = 100
    file = open("simulationData.txt", "w")
    currentTime = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                showStatsDialog()
                sys.exit()
                file.close()
            elif simulationTime == timeElapsed:
                showStatsDialog()
                sys.exit()
                file.close()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    showStatsDialog()
                    sys.exit()
                    file.close()
            # Handle control panel events
            control_panel.handle_event(event)

        screen.fill(black)
        screen.blit(background, (0, 0))  # display background in simulation

        # Your existing simulation drawing code
        for i in range(0, noOfSignals):
            if i == currentGreen:
                if currentYellow == 1:
                    signals[i].signalText = signals[i].yellow
                    screen.blit(yellowSignal, signalCoods[i])
                else:
                    signals[i].signalText = signals[i].green
                    screen.blit(greenSignal, signalCoods[i])
            else:
                if signals[i].red <= 10:
                    signals[i].signalText = signals[i].red
                else:
                    signals[i].signalText = "---"
                screen.blit(redSignal, signalCoods[i])

        # Display signal timer
        for i in range(0, noOfSignals):
            signalTexts[i] = font.render(str(signals[i].signalText), True, white, black)
            screen.blit(signalTexts[i], signalTimerCoods[i])

        # Display vehicle count
        for i in range(0, noOfSignals):
            displayText = vehicles[directionNumbers[i]]['crossed']
            vehicleCountTexts[i] = font.render(str(displayText), True, black, white)
            screen.blit(vehicleCountTexts[i], vehicleCountCoods[i])

        # Display time elapsed
        timeElapsedText = font.render(("Time Elapsed: " + str(timeElapsed)), True, black, white)
        screen.blit(timeElapsedText, timeElapsedCoods)

        # Display vehicles
        for vehicle in simulation:
            screen.blit(vehicle.image, [vehicle.x, vehicle.y])
            vehicle.move()

        # Draw control panel
        control_panel.draw(screen)

        pygame.display.update()


Main()
