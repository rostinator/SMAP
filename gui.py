import tkinter as tk
import tkinter.messagebox
import customtkinter
import summarizer as sum

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    show_more_button_text = "Show more ..."

    def __init__(self):
        super().__init__()

        self.news_summarizer = sum.NewsSummarizer()
        self.scrollable_frame_buttons = []
        self.articles_scrollable_frame_components = []
        self.actual_articles = []
        self.selected_page_index = -1

        # configure window
        self.title("News summarizer")
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        # self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure(1, weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=300)
        self.sidebar_frame.grid(row=0, column=0, pady=(5, 0), rowspan=5, sticky="nsew")
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

        self.remove_page_button = customtkinter.CTkButton(self.sidebar_frame, text="Remove Page",
                                                          command=self.remove_page_button_event)
        self.remove_page_button.grid(row=4, column=0, padx=(10, 20), pady=(0, 10), sticky="nsew")

        self.main_view_header_frame = customtkinter.CTkFrame(self)
        self.main_view_header_frame.grid(row=0, column=1, pady=(5, 0), padx=(5, 0), sticky="nsew")
        self.main_view_header_frame.grid_columnconfigure(0, weight=1)

        self.main_view_title = customtkinter.CTkLabel(self.main_view_header_frame, text="News",
                                                      font=customtkinter.CTkFont(size=25, weight="bold"))
        self.main_view_title.grid(row=0, column=0, pady=(5, 5))

        self.export_articles_button = customtkinter.CTkButton(self.main_view_header_frame, text="Export",
                                                              command=self.export_articles_button_event)
        # self.export_articles_button.grid(row=0, column=1, padx=(0, 5), pady=(5, 5))

        self.articles_scrollable_frame = customtkinter.CTkScrollableFrame(self, fg_color="transparent")
        self.articles_scrollable_frame.grid(row=1, column=1, sticky="nsew")
        self.articles_scrollable_frame.grid_columnconfigure(0, weight=1)

        self.create_articles_frames(url=None)

    def home_button_event(self):
        self.unselect_page_button()
        self.main_view_title.configure(text="News")
        print("TODO")

    def unselect_page_button(self):
        if self.selected_page_index >= 0:
            actual_selected_button = self.scrollable_frame_buttons[self.selected_page_index]
            fg_color = self.home_button.cget("fg_color")
            hover_color = self.home_button.cget("hover_color")
            actual_selected_button.configure(fg_color=fg_color, hover_color=hover_color)
            self.export_articles_button.grid_remove()
            self.selected_page_index = -1

    def select_page_button_event(self, index):
        if index + 1 <= len(self.scrollable_frame_buttons) and index != self.selected_page_index:
            newly_selected_button = self.scrollable_frame_buttons[index]
            self.unselect_page_button()

            self.selected_page_index = index
            newly_selected_button.configure(fg_color='#2554C7', hover_color='#2554C7')
            page_name = newly_selected_button.cget("text")
            self.main_view_title.configure(text=page_name)
            self.export_articles_button.grid(row=0, column=1, padx=(0, 5), pady=(5, 5))
            self.create_articles_frames(page_name)

    def add_page_button_event(self):
        dialog = customtkinter.CTkInputDialog(text="New page (Domain name):")
        url = dialog.get_input()
        if url is not None and len(url) > 0 and "https" not in url and "www" not in url:
            self.news_summarizer.add_page(sum.Page(url))
            self.scrollable_frame_buttons = []
            self.create_pages_buttons()

    def remove_page_button_event(self):
        if self.selected_page_index >= 0 and self.selected_page_index < len(self.scrollable_frame_buttons):
            selected_button = self.scrollable_frame_buttons[self.selected_page_index]
            self.news_summarizer.remove_page(selected_button.cget('text'))
            self.selected_page_index = -1
            self.scrollable_frame_buttons = []
            self.create_pages_buttons()
            self.home_button_event()

    def show_more_button_event(self, index, article_text_frame, button):
        if (button.cget("text") == self.show_more_button_text):
            article_text_frame.grid(row=2, column=0, padx=(0, 10), pady=(10, 10), sticky="nsew")
            button.configure(text="Show less")
        else:
            article_text_frame.grid_remove()
            button.configure(text=self.show_more_button_text)

    def export_articles_button_event(self):
        self.news_summarizer.save_articles_to_csv(self.main_view_title.cget("text"))

    def create_pages_buttons(self):
        for child in list(self.pages_scrollable_frame.children.values()):
            child.destroy()

        for page in self.news_summarizer.get_pages():
            index = len(self.scrollable_frame_buttons)
            button = customtkinter.CTkButton(master=self.pages_scrollable_frame, text=f"{page.url}",
                                             command=lambda i=index: self.select_page_button_event(i))
            button.grid(row=index, column=0, padx=5, pady=(5, 0), sticky="nsew")
            self.scrollable_frame_buttons.append(button)

    def create_articles_frames(self, url):
        self.articles_scrollable_frame_components = []
        for child in list(self.articles_scrollable_frame.children.values()):
            child.destroy()

        self.actual_articles = self.news_summarizer.parse_articles_from_url("novinky.cz" if url is None else url)
        for article in self.actual_articles:
            index = len(self.articles_scrollable_frame_components)
            article_frame = customtkinter.CTkFrame(master=self.articles_scrollable_frame)
            article_frame.grid(row=index, column=0, padx=(0, 10), pady=(10, 10), sticky="nsew")

            article_header_frame = customtkinter.CTkFrame(master=article_frame, fg_color="transparent")
            article_header_frame.grid(row=0, column=0, padx=(20, 0), pady=(10, 0), sticky="nsew")

            article_title_label = customtkinter.CTkLabel(master=article_header_frame, text=f"{article.title}",
                                                         justify="left", wraplength=770,
                                                         font=customtkinter.CTkFont(size=25, weight="bold"))
            article_title_label.grid(row=0, column=0, sticky="nsew")

            article_content_label = customtkinter.CTkLabel(master=article_frame, justify="left", wraplength=770, padx=0,
                                                           anchor="w",
                                                           text=f"{article.description}",
                                                           font=customtkinter.CTkFont(size=16))
            article_content_label.grid(row=1, column=0, padx=(20, 20), pady=(20, 10), sticky="nsew")

            article_text_frame = customtkinter.CTkFrame(master=article_frame, fg_color="transparent")

            grid_index = 0
            if len(article.authors) > 0:
                text = ", ".join(str(x) for x in article.authors)
                author_label = customtkinter.CTkLabel(master=article_text_frame, anchor="w", justify="left",
                                                      text=f"{text}",
                                                      font=customtkinter.CTkFont(size=14, weight="bold"))
                author_label.grid(row=grid_index, padx=(20, 0), column=0, sticky="nsew")
                grid_index += 1

            if article.site_name is not None:
                site_name_label = customtkinter.CTkLabel(master=article_text_frame, anchor="w", justify="left",
                                                         text=f"{article.site_name}",
                                                         font=customtkinter.CTkFont(size=16, weight="bold"))
                site_name_label.grid(row=grid_index, padx=(20, 0), column=0, sticky="nsew")
                grid_index += 1

            if len(article.keywords) > 0:
                text = ", ".join(str(x) for x in article.keywords)
                keywords = customtkinter.CTkLabel(master=article_text_frame, anchor="w", justify="left",
                                                  text=f"{text}",
                                                  font=customtkinter.CTkFont(size=14, slant="italic"))
                keywords.grid(row=grid_index, padx=(20, 0), column=0, sticky="nsew")
                grid_index += 1

            if article.summary:
                summary_label = customtkinter.CTkLabel(master=article_text_frame, anchor="w", justify="left",
                                                       text="Summary:",
                                                       font=customtkinter.CTkFont(size=14, weight="bold"))
                summary_label.grid(row=grid_index, padx=(20, 0), column=0, sticky="nsew")
                grid_index += 1
                summary_text_label = customtkinter.CTkLabel(master=article_text_frame, justify="left",
                                                            wraplength=800, anchor="w", padx=0,
                                                            text=f"{article.summary}",
                                                            font=customtkinter.CTkFont(size=14))
                summary_text_label.grid(row=grid_index, padx=(20, 0), column=0, sticky="nsew")
                grid_index += 1

            if len(article.text) > 0:
                article_label = customtkinter.CTkLabel(master=article_text_frame, anchor="w", justify="left",
                                                       text="Original text:",
                                                       font=customtkinter.CTkFont(size=14, weight="bold"))
                article_label.grid(row=grid_index, padx=(20, 0), pady=(10, 0), column=0, sticky="nsew")
                grid_index += 1
                for i in range(len(article.text) - 1):
                    article_text_label = customtkinter.CTkLabel(master=article_text_frame, justify="left",
                                                                wraplength=800,
                                                                anchor="w", padx=0,
                                                                text=f"{article.text[i + 1]}",
                                                                font=customtkinter.CTkFont(size=14))
                    article_text_label.grid(row=i + grid_index, column=0, padx=(20, 20),
                                            pady=(0, 10), sticky="nsew")

            button_frame = customtkinter.CTkFrame(master=article_frame, fg_color="transparent")
            button_frame.grid(row=3, column=0, sticky="nsew")

            show_more_button = customtkinter.CTkButton(master=button_frame, text=self.show_more_button_text)
            show_more_button.configure(command=lambda i=index, atf=article_text_frame, btn=show_more_button:
            self.show_more_button_event(i, atf, btn))

            show_more_button.grid(row=0, column=0, padx=(20, 0), pady=(10, 10))

            self.articles_scrollable_frame_components.append(article_frame)


if __name__ == "__main__":
    app = App()
    app.mainloop()
