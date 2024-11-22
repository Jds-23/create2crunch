import time

interval_seconds = 10

checkpoint = time.time()
d_checkpoint = None
r_checkpoint = None
count_checkpoint = None
total_checkpoint = None
iterations = 0

def get_uniscore(address):
    """Calculate uniscore based on scoring rules for contract address"""
    # Convert address to nibbles (assuming address is a hex string)
    # Skip '0x' prefix if present
    addr = address[2:] if address.startswith('0x') else address
    nibbles = [int(c, 16) for c in addr]
    
    score = 0
    
    # Count leading zeros
    leading_zeros = 0
    for n in nibbles:
        if n == 0:
            leading_zeros += 1
        else:
            break
    
    # Check if first nonzero nibble is 4
    if leading_zeros >= len(nibbles) or nibbles[leading_zeros] != 4:
        return 0  # Invalid if first nonzero nibble is not 4
    
    # Add points for leading zeros
    score += leading_zeros * 10
    
    # Check for four 4s after first nonzero
    if (leading_zeros + 4) <= len(nibbles):
        if all(n == 4 for n in nibbles[leading_zeros:leading_zeros+4]):
            score += 40
            # Check if the nibble after the four 4s is NOT a 4
            if leading_zeros + 4 < len(nibbles) and nibbles[leading_zeros+4] != 4:
                score += 20
    
    # Check if last 4 nibbles are all 4s
    if all(n == 4 for n in nibbles[-4:]):
        score += 20
    
    # Count total 4s
    score += sum(1 for n in nibbles if n == 4)
    
    return score

def get_score(row):
    try:
        # Original score from the end of the line
        original_score = int(row[116:])
        # Get contract address part (positions 70-112)
        contract_address = row[70:112]
        # Calculate uniscore
        uni_score = get_uniscore(contract_address)
        return original_score, uni_score
    except ValueError:
        return 0, 0

# print(get_uniscore('0x00000000004444d3cB22EA006470e100Eb014F2D'))

while True:
    print(f'\n\n\nruntime: {round((time.time() - checkpoint) / 60, 2)} minutes')

    with open('./efficient_addresses.txt') as f:
        content = f.readlines()

    # Modified to get both scores
    scores = [get_score(i) for i in content]
    d = [score[0] for score in scores]  # Original scores
    uni_scores = [score[1] for score in scores]  # Uniscores

    if d_checkpoint is None:
        d_checkpoint = len(d)

    d_change = len(d) - d_checkpoint

    if (iterations != 0):
        d_iterations = round(d_change/(iterations * interval_seconds), 4)
        print(
            f'valuable submissions found this run: {d_change}',
            f'or {d_iterations} per second'
        )

    r = {}
    count = {}

    for i in d:
      if i not in r:
        r[i] = i
        count[i] = 1
      else:
        r[i] += i
        count[i] += 1

    total = 0
    for i in range(max(d) + 1):
      if i in r:
        total += r[i]

    longest = max(len(str(k)) for k in count.keys())

    if total_checkpoint is None:
        total_checkpoint = total

    change = total - total_checkpoint

    if (iterations != 0):
        r_iterations = round(change/(iterations * interval_seconds), 4)
    else:
        r_iterations = 0
    print('sum of rewards this run:', change, 'or', r_iterations ,'per second')

    if d_change > 0:
        print('reward ratio this run:', round(change / d_change, 4))

    print('\ntotal valuable submissions found:', len(d))

    print('total rewards:', total)
    if len(d) > 0:
        print('total reward ratio:', round(total / len(d), 4))

    print('total submissions by amount:')
    for k, v in sorted(count.items()):
        print(f' * {str(k).rjust(longest)}: {v}')

    print('total submission rewards by %:')
    for i in range(max(d) + 1):
      if i in r:
        try:
            ratio = r[i] / total
        except ZeroDivisionError:
            ratio = 0
        print(f' * {str(i).rjust(longest)}: {round(ratio * 10000) / 100}%')

    most_valuable_index = d.index(max(d))
    print('\nmost valuable submission found:', d[most_valuable_index])
    print('found at line:', most_valuable_index + 1)
    print(' * salt:', content[most_valuable_index][:66])
    print(' * contract address:', content[most_valuable_index][70:112])

    leading_zero_bytes = 0
    for i, char in enumerate(content[most_valuable_index][72:111]):
        if i % 2 == 0:
            if (
              char == '0' and
              content[most_valuable_index][72:112][i + 1] == '0'
            ):
                leading_zero_bytes += 1
            else:
                break

    print(' * leading zero bytes:', leading_zero_bytes)

    zero_bytes = 0
    for i, char in enumerate(content[most_valuable_index][72:111]):
        if (
          i % 2 == 0 and
          char == '0' and
          content[most_valuable_index][72:112][i + 1] == '0'
        ):
            zero_bytes += 1

    print(' * total zero bytes:', zero_bytes)

    # Add uniscore statistics
    print('\nUniscore Statistics:')
    if len(uni_scores) > 0:
        print('Highest uniscore:', max(uni_scores))
        print('Average uniscore:', round(sum(uni_scores) / len(uni_scores), 2))
        
        # Find address with highest uniscore
        max_uni_index = uni_scores.index(max(uni_scores))
        print('\nHighest uniscore submission:')
        print('Score:', uni_scores[max_uni_index])
        print('Found at line:', max_uni_index + 1)
        print(' * salt:', content[max_uni_index][:66])
        print(' * contract address:', content[max_uni_index][70:112])
        
        # Distribution of uniscores
        uni_count = {}
        for score in uni_scores:
            uni_count[score] = uni_count.get(score, 0) + 1
            
        print('\nUniscore distribution:')
        for score, count in sorted(uni_count.items()):
            print(f' * {str(score).rjust(3)}: {count}')

    iterations += 1

    time.sleep(interval_seconds)
