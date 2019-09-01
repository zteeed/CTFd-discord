async def flush(selected_channel):
    discord_timestamp = None
    async for m in selected_channel.history(limit=100):
        if discord_timestamp is None:
            discord_timestamp = m.created_at
        if len(m.embeds) > 0 and hasattr(m.embeds[0], 'fields'):
            embed_msg = m.embeds[0].fields[0]
            title = embed_msg.name
            duration = (discord_timestamp - m.created_at).seconds
            if 'New challenge solved by' in title:
                pass
            elif 'FLUSH' in title and duration < 30:
                pass
            else:
                await m.delete()
        else:
            await m.delete()
    return True
