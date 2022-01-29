from server_scripts.card_loader import cardFixer


if __name__ == '__main__':
    import asyncio
    asyncio.run(cardFixer.main())
