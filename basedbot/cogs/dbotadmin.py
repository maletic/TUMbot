import re
import sqlite3

from discord.ext import commands


class DBotAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def sql(self, ctx, *, query):
        """Executes an SQL-query"""

        # Set default scope
        if ctx.guild is not None:
            scope = 'guild'
        else:
            scope = 'user'

        matches = re.match(r'`(.*)`(?: (\w+)(?:/(\d+))?)?', query)
        if not matches:
            await ctx.send("Couldn't filter out the query that should be executed.")
            return

        if matches.group(2) is not None:
            scope = matches.group(2)

        if matches.group(3) is None:
            if scope == 'guild':
                dbid = ctx.guild.id
            else:
                dbid = ctx.author.id
        else:
            dbid = matches.group(3)

        query = matches.group(1)
        try:
            with self.bot.db.get(dbid, scope) as db:
                result = [dict(row) for row in db.execute(query).fetchall()]
        except sqlite3.OperationalError as e:
            await ctx.send(f"```{e}```")
            return

        if len(result) < 1:
            await ctx.message.add_reaction('\U00002705')
            return

        await self.bot.send_table(ctx, result[0].keys(), result)

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, cog):
        """Loads a previously not loaded Cog"""

        name = self.bot.find_cog(cog)

        if name is None:
            await ctx.send(f"Cog `{cog}` could not be found.")
            return

        self.bot.load_extension(name)
        await ctx.message.add_reaction('\U00002705')

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, cog):
        """Unloads a previously loaded Cog"""

        name = self.bot.find_cog(cog)

        if name is None:
            await ctx.send(f"Cog `{cog}` could not be found.")
            return

        self.bot.unload_extension(name)
        await ctx.message.add_reaction('\U00002705')

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, cog):
        """Unloads and reloads a previously loaded Cog"""

        name = self.bot.find_cog(cog)

        if name is None:
            await ctx.send(f"Cog `{cog}` could not be found.")
            return

        self.bot.reload_extension(name)
        await ctx.message.add_reaction('\U00002705')


def setup(bot):
    bot.add_cog(DBotAdmin(bot))
