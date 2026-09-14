import matplotlib.pyplot as plt
import numpy as np
import cv2
import seaborn as sns
import pathlib
import os

from pywib.constants import EventTypes
from pywib.constants import ColumnNames
from pywib.utils.validation import validate_dataframe_keyboard
from pywib.utils.visualization.trace_strategies import get_visualization_strategy

def visualize_trace(df, stroke_indices, stroke_id, type: str = "simple", plot_name: str = None, plot: bool = True, save_path: str = None, **kwargs):
    """
    Generates (and optionally saves) a plot visualizing the trace of a stroke.

    Parameters:
        df (pd.DataFrame): DataFrame containing the stroke data with 'x', 'y and 'timeStamp' columns.
        stroke_indices (list): List of indices corresponding to the stroke in the DataFrame. Can be obtained using df.index
        stroke_id (str): Identifier for the stroke to be displayed in the title.
        type (str): The type of visualization strategy to use. Options are: "simple", "info", "optimal_line", "full". 
        plot_name (str, optional): If provided, saves the plot to this file path.
        plot (bool): Whether to display the plot.
        **kwargs: Additional arguments to pass to the visualization strategy.
    """
    stroke_data = df.loc[stroke_indices]
    
    # We pass kwargs to get_visualization_strategy which forwards them to the strategy constructor
    # For standardized, this means we can pass image_size and target_scale
    strategy = get_visualization_strategy(type, **kwargs)
    
    # We get the required figure size from the strategy
    figsize = strategy.get_figsize()
    fig, ax = plt.subplots(figsize=figsize)
    
    strategy.apply(ax, stroke_data, stroke_id)

    if plot_name:
        file_path = os.path.join(save_path, plot_name) if save_path else plot_name
        plt.savefig(file_path, bbox_inches='tight', dpi=300)

    if plot:
        plt.show()
    else:
        plt.close(fig)

def video_from_trace(df, user_id, outfile: str, width=640, height=480, fps=30, colored=False):
    """
    Generates a video visualizing the mouse trace of a user.
    
    Parameters:
        df (pd.DataFrame): DataFrame containing the mouse trace data with 'x', 'y', 'eventType', and 'sessionId' columns.
        user_id (str/int): Identifier of the user whose trace is to be visualized.
        outfile (str): Path to save the output video file.
        width (int): Width of the video frame.
        height (int): Height of the video frame.
        fps (int): Frames per second for the video.
        colored (bool): If True, applies a temperature gradient (green to red) to the trajectory line.
    Returns:
        None: Saves the video file to the specified path.
    """
    user_data = df[df[ColumnNames.SESSION_ID] == user_id].sort_values(ColumnNames.TIME_STAMP)
    xs = user_data[ColumnNames.X].values
    ys = user_data[ColumnNames.Y].values
    eventType = user_data[ColumnNames.EVENT_TYPE].values
    n = len(xs)
    # Nombre del vídeo
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(outfile, fourcc, fps, (width, height))
    
    # Generar frames
    frame = np.ones((height, width, 3), dtype=np.uint8) * 255  # fondo blanco
    last_x, last_y = xs[0], ys[0]
    for i in range(1, n):
        # Calculate color based on progress if colored mode is enabled
        if colored:
            # Temperature gradient: green (0, 255, 0) -> yellow -> red (0, 0, 255)
            progress = i / (n - 1)
            green = int(255 * (1 - progress))
            red = int(255 * progress)
            line_color = (0, green, red)  # BGR format
        else:
            line_color = (0, 0, 255)  # Default red
        
        # Dibujar línea de movimiento
        if xs[i] <= 0 or ys[i] <= 0 or xs[i] > width or ys[i] > height:
            # Coordenadas fuera de la pantalla, no dibujar
            pass
        elif xs[i-1] <= 0 or ys[i-1] <= 0 or xs[i-1] > width or ys[i-1] > height:
            # Coordenadas anteriores fuera de la pantalla
            if(last_x > 0 and last_y > 0):
                cv2.line(frame, (last_x, last_y), (xs[i], ys[i]), color=line_color, thickness=2)
        else:
            cv2.line(frame, (xs[i-1], ys[i-1]), (xs[i], ys[i]), color=line_color, thickness=2)
        
        # Actualizar última posición válida a la posición actual si es válida (dentro de la pantalla)
        if xs[i] > 0 and ys[i] > 0 and xs[i] <= width and ys[i] <= height:
            last_x, last_y = xs[i], ys[i]

        # Dibujar clics
        if eventType[i] == EventTypes.EVENT_ON_CLICK or (eventType[i-1] == EventTypes.EVENT_ON_MOUSE_DOWN and eventType[i] == EventTypes.EVENT_ON_MOUSE_UP):
            cv2.circle(frame, (last_x, last_y), radius=5, color=(0, 0, 255), thickness=-1)
        elif eventType[i] == EventTypes.EVENT_KEY_DOWN or eventType[i] == EventTypes.EVENT_KEY_UP:
            # This event has coordinates (0,0) or (-1,-1)
            cv2.rectangle(frame, (last_x-5, last_y-5), (last_x+5, last_y+5), color=(255, 0, 0), thickness=-1)
        elif eventType[i] == EventTypes.EVENT_WINDOW_SCROLL:
            # This event has coordinates (0,0) or (-1,-1)
            pts = np.array([(last_x, last_y-5), (last_x-5, last_y+5), (last_x+5, last_y+5)], np.int32)
            cv2.polylines(frame, [pts], True, (255, 0, 0), 2)
        else:
            # Unknown or unhandled event type
            pass
        
        # Escribir frame en vídeo
        video.write(frame.copy())
    
    video.release()
    print(f"Video generated for user {user_id}: {outfile}")

def keyboard_heatmap(df, session_id=None):

    validate_dataframe_keyboard(df)

    if session_id is not None:
        df = df[df[ColumnNames.SESSION_ID] == session_id]

    # Only count keydown events
    df = df[df[ColumnNames.EVENT_TYPE] == EventTypes.EVENT_KEY_DOWN]

    # ---- Convert ASCII to character ----
    df = df.copy()

    # Drop null / invalid ascii
    df = df[df[ColumnNames.KEY_CODE_EVENT].notna()]

    if df.empty:
        # TODO warn?
        return

    # Convert ASCII integer → character
    df["char"] = df[ColumnNames.KEY_CODE_EVENT].astype(int).apply(chr)

    # Normalize to lowercase (so A and a merge)
    df["char"] = df["char"].apply(str.lower)

    key_counts = df["char"].value_counts()

    # ---- FULL STANDARD QWERTY LAYOUT (ANSI) ----
    layout = [
        ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "="],
        ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]"],
        ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'"],
        ["z", "x", "c", "v", "b", "n", "m", ",", ".", "/"],
        ["space"]
    ]

    # Determine max width for consistent matrix
    max_cols = max(len(row) for row in layout)

    heatmap_data = []
    annotations = []

    
    for row in layout:
        data_row = []
        label_row = []

        for key in row:
            if key == "space":
                count = key_counts.get(" ", 0)
                label = "Space"
            else:
                count = key_counts.get(key, 0)
                label = key.upper()
            print(f"Count: {count}, Label: {label}, key: {key}")
            data_row.append(count)
            label_row.append(f"{label}\n{count}")

        while len(data_row) < max_cols:
            data_row.append(np.nan)
            label_row.append("")

        heatmap_data.append(data_row)
        annotations.append(label_row)

    heatmap_data = np.array(heatmap_data)

    plt.figure(figsize=(18, 6))
    sns.heatmap(
        heatmap_data,
        annot=np.array(annotations),
        fmt="",
        cmap="Reds",
        linewidths=0.5,
        vmin=0,
        linecolor="gray",
        cbar=True
    )
    
    plt.title("Keyboard Usage Heatmap (ASCII / keyCodeEvent)")
    plt.xticks([])
    plt.yticks([])
    plt.show()
        