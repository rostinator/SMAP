import tkinter as tk
import tkinter.messagebox
import customtkinter
import summarizer as sum

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.news_summarizer = sum.NewsSummarizer()
        self.scrollable_frame_buttons = []
        self.selected_page_index = -1

        # configure window
        self.title("News summarizer")
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        # self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure(0, weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=300)
        self.sidebar_frame.grid(row=0, column=0, pady=(5, 0), rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(2, weight=1)
        # self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Summarizer",
                                                 font=customtkinter.CTkFont(size=25, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(5, 20))

        self.home_button = customtkinter.CTkButton(self.sidebar_frame, text="Home", command=self.home_button_event)
        self.home_button.grid(row=1, column=0, padx=(10, 20), pady=(0, 10), sticky="nsew")

        self.pages_scrollable_frame = customtkinter.CTkScrollableFrame(self.sidebar_frame)
        self.pages_scrollable_frame.grid(row=2, column=0, sticky="nsew")
        self.pages_scrollable_frame.grid_columnconfigure(0, weight=1)

        self.create_pages_buttons()

        self.add_page_button = customtkinter.CTkButton(self.sidebar_frame, text="Add Page",
                                                       command=self.add_page_button_event)
        self.add_page_button.grid(row=3, column=0, padx=(10, 20), pady=(20, 10), sticky="nsew")

        self.articles_scrollable_frame = customtkinter.CTkScrollableFrame(self, fg_color="transparent")
        self.articles_scrollable_frame.grid(row=0, column=1, sticky="nsew")
        self.articles_scrollable_frame.grid_columnconfigure(0, weight=1)

        self.articles_scrollable_frame_components = []

        for article in self.news_summarizer.parse_articles_from_url("https://www.novinky.cz"):
            article_frame = customtkinter.CTkFrame(master=self.articles_scrollable_frame)
            article_frame.grid(row=len(self.articles_scrollable_frame_components), column=0, padx=(0, 10),
                               pady=(10, 10), sticky="nsew")
            article_frame.grid_columnconfigure(0, weight=0)

            article_header_frame = customtkinter.CTkFrame(master=article_frame, fg_color="transparent")
            article_header_frame.grid(row=0, column=0, padx=(20, 0), pady=(10, 0), sticky="nsew")

            article_title_label = customtkinter.CTkLabel(master=article_header_frame, text=f"{article.title}",
                                                         justify="left", wraplength=800,
                                                         font=customtkinter.CTkFont(size=25, weight="bold"))
            article_title_label.grid(row=0, column=0, sticky="nsew")

            article_content_label = customtkinter.CTkLabel(master=article_frame, justify="left", wraplength=770, padx=0,
                                                           anchor="w",
                                                           text=f"{article.description}",
                                                           font=customtkinter.CTkFont(size=16))
            article_content_label.grid(row=1, column=0, padx=(20, 20), pady=(20, 10), sticky="nsew")

            article_text_frame = customtkinter.CTkFrame(master=article_frame, fg_color="transparent")
            article_text_frame.grid(row=2, column=0, padx=(0, 10), pady=(10, 10), sticky="nsew")

            for i in range(len(article.text) - 1):
                article_text_label = customtkinter.CTkLabel(master=article_text_frame, justify="left", wraplength=800,
                                                            anchor="w", padx=0,
                                                            text=f"{article.text[i + 1]}",
                                                            font=customtkinter.CTkFont(size=14))
                article_text_label.grid(row=i, column=0, padx=(20, 20), pady=(0, 10), sticky="nsew")

            self.articles_scrollable_frame_components.append(article_frame)

    def home_button_event(self):
        self.unselect_page_button()
        print("TODO")

    def unselect_page_button(self):
        if self.selected_page_index >= 0:
            actual_selected_button = self.scrollable_frame_buttons[self.selected_page_index]
            fg_color = self.home_button.cget("fg_color")
            hover_color = self.home_button.cget("hover_color")
            actual_selected_button.configure(fg_color=fg_color, hover_color=hover_color)
            self.selected_page_index = -1

    def select_page_button_event(self, index):
        if (index + 1 <= len(self.scrollable_frame_buttons)):
            newly_selected_button = self.scrollable_frame_buttons[index]
            self.unselect_page_button()

            self.selected_page_index = index
            newly_selected_button.configure(fg_color='#2554C7', hover_color='#2554C7')

    def add_page_button_event(self):
        dialog = customtkinter.CTkInputDialog(text="New page (Domain name):")
        url = dialog.get_input()
        if url is not None and len(url) > 0 and "https" not in url and "www" not in url:
            self.news_summarizer.add_page(sum.Page(url))
            self.scrollable_frame_buttons = []
            self.create_pages_buttons()

    def create_pages_buttons(self):
        for page in self.news_summarizer.get_pages():
            index = len(self.scrollable_frame_buttons)
            button = customtkinter.CTkButton(master=self.pages_scrollable_frame, text=f"{page.url}",
                                             command=lambda i=index: self.select_page_button_event(i))
            button.grid(row=index, column=0, padx=5, pady=(5, 0), sticky="nsew")
            self.scrollable_frame_buttons.append(button)


if __name__ == "__main__":
    app = App()
    app.mainloop()
