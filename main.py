import asyncio
import tkinter as tk
from tkinter import messagebox, ttk
import platform
from receive import receive_transcriptions
from process import append_to_transcript, send_transcript_content, reset_transcript, get_transcript_buffer

if platform.system() == "Darwin":
    from tkmacosx import Button as CustomButton
else:
    from tkinter import Button as CustomButton

class TranscriptApp:
    def __init__(self, root, loop):
        self.root = root
        self.loop = loop
        self.root.title("Shounenba")
        self.root.configure(bg='black')

        # Define colors
        bg_color = 'black'
        fg_color = 'pink'
        button_bg_color = 'pink'
        button_fg_color = 'black'
        text_bg_color = 'black'
        text_fg_color = 'pink'
        
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=1, fill='both')

        
        self.main_frame = tk.Frame(self.notebook, bg=bg_color)
        self.notebook.add(self.main_frame, text='Main')
        
        
        self.buffer_display_label = tk.Label(self.main_frame, text="Transcript Buffer:", bg=bg_color, fg=fg_color)
        self.buffer_display_label.pack(pady=5)
        self.buffer_display = tk.Text(self.main_frame, height=10, bg=text_bg_color, fg=text_fg_color)
        self.buffer_display.pack(fill='both', expand=True, pady=5)

        self.reset_buffer_button = CustomButton(self.main_frame, text="Reset Transcript", command=self.on_reset_buffer,
                                                bg=button_bg_color, fg=button_fg_color)
        self.reset_buffer_button.pack(pady=5)

        self.response_display = tk.Text(self.main_frame, height=20, bg=text_bg_color, fg=text_fg_color)
        self.response_display.pack(fill='both', expand=True, pady=20)

        self.send_button = CustomButton(self.main_frame, text="Send", command=self.on_send_transcript,
                                        bg=button_bg_color, fg=button_fg_color)
        self.send_button.pack(pady=20)

        


    def on_reset_buffer(self):
        reset_transcript()
        self.loop.call_soon_threadsafe(self.update_buffer_display)

    def on_send_transcript(self):
        self.clear_response_display()
        self.loop.call_soon_threadsafe(self.clear_buffer_display)
        asyncio.run_coroutine_threadsafe(self.send_transcript(), self.loop)

    def on_quit(self):
        self.loop.stop()

    def clear_response_display(self):
        self.response_display.delete('1.0', tk.END)

    def clear_buffer_display(self):
        self.buffer_display.delete('1.0', tk.END)

    async def send_transcript(self):
        async for response in send_transcript_content():
            self.loop.call_soon_threadsafe(self.update_response_display, response)
        #self.loop.call_soon_threadsafe(lambda: messagebox.showinfo("Info", "Transcript sent successfully!"))

    def update_response_display(self, message):
        if isinstance(message, str):
            self.response_display.insert(tk.END, message)
            self.response_display.see(tk.END)
        else:
            print("Unexpected message type:", type(message))

    def update_buffer_display(self):
        self.clear_buffer_display()
        self.buffer_display.insert(tk.END, get_transcript_buffer())
        self.buffer_display.see(tk.END)

async def main():
    async def transcript_callback(transcript):
        append_to_transcript(transcript)
        loop.call_soon_threadsafe(app.update_buffer_display)
    
    root = tk.Tk()
    loop = asyncio.get_event_loop()
    app = TranscriptApp(root, loop)

    receiver_task = asyncio.create_task(receive_transcriptions(transcript_callback))

    async def run_tk(root):
        while True:
            root.update()
            await asyncio.sleep(0.01)

    await asyncio.gather(receiver_task, run_tk(root))

if __name__ == "__main__":
    asyncio.run(main())
