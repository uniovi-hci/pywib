import matplotlib.pyplot as plt
import numpy as np
import cv2
import seaborn as sns

from pywib.constants import EventTypes
from pywib.constants import ColumnNames
from pywib.utils.validation import validate_dataframe_keyboard

def visualize_trace(df, stroke_indices, stroke_id, plot_name: str = None, plot: bool = True, show_info: bool = False, show_optimal_line: bool = False):
    """
    Generates (and optionally saves) a plot visualizing the trace of a stroke.

    Parameters:
        df (pd.DataFrame): DataFrame containing the stroke data with 'x', 'y and 'timeStamp' columns.
        stroke_indices (list): List of indices corresponding to the stroke in the DataFrame. Can be obtained using df.index
        stroke_id (str): Identifier for the stroke to be displayed in the title.
        plot_name (str, optional): If provided, saves the plot to this file path.
        plot (bool): Whether to display the plot.
    """
    stroke_data = df.loc[stroke_indices]
    plt.figure(figsize=(10, 8))
    plt.plot(stroke_data[ColumnNames.X], stroke_data[ColumnNames.Y], 'b-o', linewidth=2, markersize=4, label='Real trace')

    x_start, y_start = stroke_data[ColumnNames.X].iloc[0], stroke_data[ColumnNames.Y].iloc[0]
    x_end, y_end = stroke_data[ColumnNames.X].iloc[-1], stroke_data[ColumnNames.Y].iloc[-1]
    
    if(show_optimal_line):
        plt.plot([x_start, x_end], [y_start, y_end], 'r--', linewidth=2, label='Optimal trace')

        plt.plot(x_start, y_start, 'go', markersize=8, label='Start')
        plt.plot(x_end, y_end, 'ro', markersize=8, label='End')

  
    if(show_info):
        duration = stroke_data[ColumnNames.TIME_STAMP].iloc[-1] - stroke_data[ColumnNames.TIME_STAMP].iloc[0]
        plt.xlabel('X (px)')
        plt.ylabel('Y (px)')
        plt.title(f'Trace {stroke_id} - Duration: {duration:.0f}ms - Points: {len(stroke_data)}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.gca().invert_yaxis()
    else:
        plt.axis('off')

    if plot_name:
        plt.savefig(plot_name, bbox_inches='tight', dpi=300)

    if plot:
        plt.show()
    else:
        plt.close()

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
    """
    Generates a heatmap visualizing the frequency of key presses for a given session or for all sessions in the DataFrame.
    The type of keyboard represented is a standard QWERTY layout (ANSI), and the heatmap shows the frequency of key presses for each key.
    To change the keyboard layout, you can modify the 'layout' variable in the function.
    """

    validate_dataframe_keyboard(df)

    if session_id is not None:
        df = df[df[ColumnNames.SESSION_ID] == session_id]

    # Only count keydown events
    df = df[df[ColumnNames.EVENT_TYPE] == EventTypes.EVENT_KEY_DOWN]

    # ---- Convert ASCII to character ----
    df = df.copy()

    # Drop null / invalid ascii
    df = df[df[ColumnNames.KEY_VALUE].notna()]

    if df.empty:
        # TODO warn?
        return

    # Convert ASCII integer → character
    df["char"] = df[ColumnNames.KEY_VALUE]

    # Normalize to lowercase (so A and a merge)
    df["char"] = df["char"].apply(str.lower)

    key_counts = df["char"].value_counts()

    layout = [
            ["escape", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12"],
            ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "backspace"],
            ["tab", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "[", "]", "\\"],
            ["capslock", "a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "'", "enter"],
            ["shift", "z", "x", "c", "v", "b", "n", "m", ",", ".", "/", "shift"],
            ["control", "meta", "alt", "space", "altgraph", "arrowleft", "arrowup", "arrowdown", "arrowright"]
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
                label = "space"
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
    
    plt.title("Keyboard Usage Heatmap (ASCII / keyCode)")
    plt.xticks([])
    plt.yticks([])
    plt.show()
        