# binary_search 筆記

<!-- 在此加入這個類別的筆記 -->

### [l, r) 左閉右開 Template

```cpp
while (l < r) {                     // 條件是 l < r，當 l == r 時跳出
    int mid = l + (r - l) / 2;
    if (nums[mid] <= target)        // 當 nums[mid] <= target，表示答案在右邊（不含 mid）
        l = mid + 1;
    else
        r = mid;
}
// 若找不到，l == r 為跳出點


```

### 當跳出迴圈
- l == r，是第一個 > target 的 index
- 如果沒有比 target 大的數，l 會等於 nums.size()（越界）