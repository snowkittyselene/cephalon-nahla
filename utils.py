import discord


class PaginationView(discord.ui.View):
    def __init__(self, items, info, items_per_page, timeout, generate_base):
        super().__init__(timeout=timeout)
        self.start = 0
        self.items = items
        self.info = info
        self.items_per_page = items_per_page
        self.embed, self.message = None, None
        self.generate_base = generate_base

    def update_buttons(self):
        if self.start == 0:
            self.children[0].disabled = True
        elif self.start + self.items_per_page >= len(self.items):
            self.children[1].disabled = True
        else:
            self.children[0].disabled = False
            self.children[1].disabled = False

    async def on_timeout(self):
        self.clear_items()
        await self.message.edit(embed=self.embed, view=self)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.gray, disabled=True)
    async def prev_page(self, ctx: discord.Interaction, btn: discord.ui.Button):
        await ctx.response.defer()
        self.start -= self.items_per_page
        self.start = 0 if self.start < 0 else self.start
        self.embed = await self.generate_base(self.start, self.items, self.info)
        self.update_buttons()
        self.message = await ctx.message.edit(embed=self.embed, view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.gray)
    async def next_page(self, ctx: discord.Interaction, btn: discord.ui.Button):
        await ctx.response.defer()
        self.start = (
            self.start + self.items_per_page
            if self.start + self.items_per_page < len(self.items)
            else self.start
        )
        self.embed = await self.generate_base(self.start, self.items, self.info)
        self.update_buttons()
        self.message = await ctx.message.edit(embed=self.embed, view=self)
