# binary_search 筆記

<!-- 在此加入這個類別的筆記 -->

### 閉區間 Template
```clike=
int l = 0, r = nums.size() - 1;
while (l <= r) {
    int mid = l + (r - l) / 2;
    if (nums[mid] == target)
        return mid;
    else if (nums[mid] < target)
        l = mid + 1;
    else
        r = mid - 1;
}
// 若找不到，l > r 時跳出

```