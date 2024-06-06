import numpy as np


def levenshtein_distance(s1, s2):
    len_s1, len_s2 = len(s1), len(s2)
    dp = np.zeros((len_s1 + 1, len_s2 + 1))

    for i in range(len_s1 + 1):
        dp[i][0] = i
    for j in range(len_s2 + 1):
        dp[0][j] = j

    for i in range(1, len_s1 + 1):
        for j in range(1, len_s2 + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    
    return dp[len_s1][len_s2]


def find_best_match_position(source_text, target_text):
    min_distance = float('inf')
    best_position = -1

    for i in range(len(source_text) - len(target_text) + 1):
        window = source_text[i:i + len(target_text)]
        distance = levenshtein_distance(window, target_text)
        if distance < min_distance:
            min_distance = distance
            best_position = i
    
    return best_position, best_position+len(target_text)
