import asyncio
import sys

from tasks.main import start_user_withdraw


async def main():
    try:
        user_action: int = input('Choose your action:\n'
                                 '    1. Withdraw with user delay.\n'
                                 '    2. Queue withdraw. (without delay)\n'
                                 '[+] Your choice: ')
        while not user_action.isdigit():
            print('The entered value should be a number! Please try again.')
            user_action = input('[+] Your choise: ')
        if user_action in ['1', '2']:
            await start_user_withdraw(user_action)
        else:
            print('User action must be 1 or 2')
            sys.exit(0)
    except KeyboardInterrupt:
        print()
        input(f'\nPress Enter to exit.\n')

if __name__ == '__main__':
    print('Starknet withdraw software')
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
